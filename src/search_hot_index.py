import argparse, json, sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"cache"/"github_hot.sqlite"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit",type=int,default=20)
    ap.add_argument("--include-archived",action="store_true")
    ap.add_argument("--license-required",action="store_true")
    args=ap.parse_args()
    if not DB.exists(): raise SystemExit("FAIL: hot index not built")
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    where=["repos_fts MATCH ?"]
    params=[args.query]
    if not args.include_archived: where.append("r.archived=0")
    if args.license_required: where.append("r.license_spdx IS NOT NULL AND r.license_spdx NOT IN ('NOASSERTION','OTHER')")
    sql=f"""SELECT r.id,r.full_name,r.html_url,r.description,r.language,r.license_spdx,r.stars,r.forks,r.updated_at,r.archived
FROM repos_fts f JOIN repos r ON r.id=f.rowid
WHERE {' AND '.join(where)}
ORDER BY bm25(repos_fts), r.stars DESC
LIMIT ?"""
    params.append(args.limit)
    rows=[dict(x) for x in con.execute(sql,params).fetchall()]
    con.close()
    print(json.dumps({"status":"PASS","query":args.query,"count":len(rows),"results":rows},ensure_ascii=False))

if __name__=="__main__":
    main()
