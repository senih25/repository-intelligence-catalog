import argparse, gzip, json, sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/"config"/"settings.json").read_text(encoding="utf-8"))
DB=ROOT/"cache"/"github_hot.sqlite"
STAGING=ROOT/"staging"
DRIVE_RAW=Path(CFG["storage"].get("mounted_cloud_root",""))/"raw"

SCHEMA="""
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
CREATE TABLE IF NOT EXISTS repos(
 id INTEGER PRIMARY KEY,
 full_name TEXT NOT NULL,
 html_url TEXT NOT NULL,
 description TEXT,
 owner TEXT,
 fork INTEGER NOT NULL DEFAULT 0,
 archived INTEGER NOT NULL DEFAULT 0,
 disabled INTEGER NOT NULL DEFAULT 0,
 language TEXT,
 license_spdx TEXT,
 topics TEXT,
 stars INTEGER NOT NULL DEFAULT 0,
 forks INTEGER NOT NULL DEFAULT 0,
 open_issues INTEGER NOT NULL DEFAULT 0,
 created_at TEXT,
 updated_at TEXT,
 pushed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_repos_updated ON repos(updated_at);
CREATE INDEX IF NOT EXISTS idx_repos_stars ON repos(stars DESC);
CREATE INDEX IF NOT EXISTS idx_repos_language ON repos(language);
CREATE INDEX IF NOT EXISTS idx_repos_license ON repos(license_spdx);
CREATE VIRTUAL TABLE IF NOT EXISTS repos_fts USING fts5(full_name,description,topics,content='repos',content_rowid='id');
"""

UPSERT="""INSERT INTO repos(id,full_name,html_url,description,owner,fork,archived,disabled,language,license_spdx,topics,stars,forks,open_issues,created_at,updated_at,pushed_at)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
ON CONFLICT(id) DO UPDATE SET
 full_name=excluded.full_name,html_url=excluded.html_url,description=excluded.description,owner=excluded.owner,
 fork=excluded.fork,archived=excluded.archived,disabled=excluded.disabled,language=excluded.language,
 license_spdx=excluded.license_spdx,topics=excluded.topics,stars=excluded.stars,forks=excluded.forks,
 open_issues=excluded.open_issues,created_at=excluded.created_at,updated_at=excluded.updated_at,pushed_at=excluded.pushed_at"""

def row(r):
    return (r.get("id"),r.get("full_name"),r.get("html_url"),r.get("description"),r.get("owner"),
            int(bool(r.get("fork"))),int(bool(r.get("archived"))),int(bool(r.get("disabled"))),
            r.get("language"),r.get("license_spdx")," ".join(r.get("topics") or []),
            r.get("stars") or 0,r.get("forks") or 0,r.get("open_issues") or 0,
            r.get("created_at"),r.get("updated_at"),r.get("pushed_at"))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--limit",type=int,default=250000)
    ap.add_argument("--reset",action="store_true")
    args=ap.parse_args()
    DB.parent.mkdir(parents=True,exist_ok=True)
    if args.reset and DB.exists(): DB.unlink()
    con=sqlite3.connect(DB)
    con.executescript(SCHEMA)
    inserted=0
    files={}
    for base in (DRIVE_RAW,STAGING):
        if base.exists():
            for p in base.glob("repos-*.jsonl.gz"):
                files[p.name]=p
    for p in [files[k] for k in sorted(files)]:
        with gzip.open(p,"rt",encoding="utf-8") as f:
            batch=[]
            for line in f:
                if not line.strip(): continue
                batch.append(row(json.loads(line)))
                if len(batch)>=1000:
                    con.executemany(UPSERT,batch); inserted+=len(batch); batch=[]
                    if args.limit and inserted>=args.limit: break
            if batch and (not args.limit or inserted<args.limit):
                if args.limit: batch=batch[:max(0,args.limit-inserted)]
                con.executemany(UPSERT,batch); inserted+=len(batch)
        con.commit()
        if args.limit and inserted>=args.limit: break
    con.execute("INSERT INTO repos_fts(repos_fts) VALUES('rebuild')")
    con.commit()
    total=con.execute("SELECT COUNT(*) FROM repos").fetchone()[0]
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    con.close()
    db_bytes=DB.stat().st_size if DB.exists() else 0
    print(json.dumps({"status":"PASS","processed":inserted,"total":total,"db":str(DB),"bytes":db_bytes}))

if __name__=="__main__":
    main()
