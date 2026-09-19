import argparse, gzip, hashlib, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "settings.json"
STATE_PATH = ROOT / "staging" / "checkpoint.json"
QUEUE_PATH = ROOT / "staging" / "cloud_queue.jsonl"

def load_cfg():
    return json.loads(CFG_PATH.read_text(encoding="utf-8"))

def dir_size(path: Path):
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())

def sha256_file(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024), b""): h.update(b)
    return h.hexdigest()

def request_page(endpoint, since, per_page, headers, retries=3):
    q=urllib.parse.urlencode({"since": since, "per_page": per_page})
    url=f"{endpoint}?{q}"
    last=None
    for attempt in range(retries):
        req=urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data=json.loads(r.read().decode("utf-8"))
                return data, dict(r.headers)
        except urllib.error.HTTPError as e:
            last=e
            if e.code in (403,429):
                reset=e.headers.get("X-RateLimit-Reset")
                if reset:
                    wait=max(0, int(reset)-int(time.time())+1)
                    if wait <= 120:
                        time.sleep(wait); continue
                raise RuntimeError(f"RATE_LIMITED status={e.code}; stop safely and resume later") from e
            if 500 <= e.code < 600 and attempt < retries-1:
                time.sleep(2**attempt); continue
            raise
        except Exception as e:
            last=e
            if attempt < retries-1:
                time.sleep(2**attempt); continue
            raise
    raise last

def compact_repo(x):
    lic=x.get("license") or {}
    owner=x.get("owner") or {}
    return {
        "id": x.get("id"),
        "full_name": x.get("full_name"),
        "html_url": x.get("html_url"),
        "description": x.get("description"),
        "owner": owner.get("login"),
        "fork": bool(x.get("fork")),
        "archived": bool(x.get("archived")),
        "disabled": bool(x.get("disabled")),
        "language": x.get("language"),
        "license_spdx": lic.get("spdx_id") if isinstance(lic,dict) else None,
        "topics": x.get("topics") or [],
        "stars": x.get("stargazers_count") or 0,
        "forks": x.get("forks_count") or 0,
        "open_issues": x.get("open_issues_count") or 0,
        "created_at": x.get("created_at"),
        "updated_at": x.get("updated_at"),
        "pushed_at": x.get("pushed_at")
    }

def enqueue(path: Path, count: int, first_id, last_id):
    if QUEUE_PATH.exists():
        for line in QUEUE_PATH.read_text(encoding="utf-8",errors="ignore").splitlines():
            try:
                if json.loads(line).get("path") == str(path):
                    return
            except Exception:
                pass
    rec={"path":str(path),"rows":count,"bytes":path.stat().st_size,
         "sha256":sha256_file(path),"first_id":first_id,"last_id":last_id,
         "status":"READY_FOR_CLOUD_UPLOAD"}
    with QUEUE_PATH.open("a",encoding="utf-8") as f:
        f.write(json.dumps(rec,ensure_ascii=False)+"\n")

def main():
    cfg=load_cfg(); gh=cfg["github"]; st=cfg["storage"]
    ap=argparse.ArgumentParser()
    ap.add_argument("--max-repos", type=int, default=1000)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--fresh", action="store_true")
    args=ap.parse_args()
    if args.full and args.max_repos != 1000:
        pass
    elif args.full:
        args.max_repos=0
    if args.max_repos == 0 and not args.full:
        raise SystemExit("FAIL: unlimited harvest requires --full")
    if args.full and st["cloud_soft_quota_gb"] <= 0:
        raise SystemExit("FAIL: full harvest requires positive quota guard")

    token=os.getenv(gh["token_env"],"").strip()
    headers={"Accept":"application/vnd.github+json","User-Agent":gh["user_agent"],
             "X-GitHub-Api-Version":"2022-11-28"}
    if token: headers["Authorization"]=f"Bearer {token}"

    staging=ROOT/"staging"; staging.mkdir(parents=True,exist_ok=True)
    state={"since":0,"total":0,"chunk_no":1,"chunk_rows":0}
    if STATE_PATH.exists() and not args.fresh:
        state.update(json.loads(STATE_PATH.read_text(encoding="utf-8")))
    if args.fresh:
        for p in staging.glob("repos-*.jsonl.gz"): p.unlink()
        for p in (STATE_PATH,QUEUE_PATH):
            if p.exists(): p.unlink()

    max_bytes=int(st["local_staging_gb"]*1024**3)
    chunk_limit=int(st["chunk_rows"])

    if not args.fresh and state.get("chunk_rows",0):
        prior=staging/f"repos-{state['chunk_no']:06d}.jsonl.gz"
        if prior.exists():
            first_id=None
            try:
                with gzip.open(prior,"rt",encoding="utf-8") as pf:
                    first_id=json.loads(next(pf))["id"]
            except Exception:
                pass
            enqueue(prior,int(state["chunk_rows"]),first_id,state["since"])
            state["chunk_no"] += 1
            state["chunk_rows"] = 0
            STATE_PATH.write_text(json.dumps(state,indent=2),encoding="utf-8")

    current=None; current_count=0; current_first=None; last_headers={}

    def open_chunk():
        nonlocal current,current_count,current_first
        current=staging/f"repos-{state['chunk_no']:06d}.jsonl.gz"
        current_count=0; current_first=None
        return gzip.open(current,"at",encoding="utf-8")

    fh=open_chunk()
    try:
        while True:
            if args.max_repos and state["total"] >= args.max_repos: break
            if dir_size(staging) >= max_bytes:
                print("STOP: local staging quota reached",file=sys.stderr); break
            page,hdr=request_page(gh["endpoint"],state["since"],gh["per_page"],headers)
            last_headers=hdr
            if not page: break
            for raw in page:
                rec=compact_repo(raw)
                if current_first is None: current_first=rec["id"]
                fh.write(json.dumps(rec,ensure_ascii=False)+"\n")
                current_count += 1; state["total"] += 1
                state["since"]=int(rec["id"] or state["since"])
                state["chunk_rows"]=current_count
                if current_count >= chunk_limit:
                    fh.close(); enqueue(current,current_count,current_first,state["since"])
                    state["chunk_no"] += 1; state["chunk_rows"]=0
                    STATE_PATH.write_text(json.dumps(state,indent=2),encoding="utf-8")
                    fh=open_chunk()
                if args.max_repos and state["total"] >= args.max_repos: break
            STATE_PATH.write_text(json.dumps(state,indent=2),encoding="utf-8")
        fh.close()
        if current and current.exists() and current_count:
            enqueue(current,current_count,current_first,state["since"])
        elif current and current.exists() and current.stat().st_size==0:
            current.unlink()
    finally:
        try: fh.close()
        except: pass
    out={"status":"PASS","total":state["total"],"since":state["since"],
         "authenticated":bool(token),"rate_remaining":last_headers.get("X-RateLimit-Remaining"),
         "staging_bytes":dir_size(staging),"queue":str(QUEUE_PATH)}
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__":
    main()
