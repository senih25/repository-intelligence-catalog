import csv, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/'sample'/'curated_repositories.csv'
SCHEMA=ROOT/'schema'/'repository.schema.json'

rows=list(csv.DictReader(CSV.open(encoding='utf-8')))
schema=json.loads(SCHEMA.read_text(encoding='utf-8'))
required=set(schema['required'])
assert len(rows)==15, f'expected 15 rows, got {len(rows)}'
assert required.issubset(rows[0].keys())
assert len({r['repo_id'] for r in rows})==len(rows)
assert all(r['html_url'].startswith('https://github.com/') for r in rows)
assert all(r['archived'] in {'True','False','true','false'} for r in rows)
print(json.dumps({'status':'PASS','rows':len(rows),'unique_repo_ids':len(rows),'schema_required':sorted(required)}))
