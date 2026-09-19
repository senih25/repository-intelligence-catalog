# Methodology

## Discovery grain
One GitHub repository ID is one inventory record.

## Two-stage strategy
1. Cheap discovery: enumerate/search repository metadata without cloning.
2. Expensive enrichment: fetch live license, stars, language, dates and maintenance signals only for shortlisted candidates.

## Project workflow
Project need → deterministic filters → search → top 20 → evidence review → top 1–3 → REUSE / ADAPT / REFERENCE / AVOID.

## Evidence rules
- Stars are discovery signals, not proof of quality.
- Archived repositories are avoided by default.
- Missing/unclear license blocks reuse.
- Current repository state is revalidated before integration.
- Security/dependency review is separate from popularity.

## Storage
Bulk shards stay outside Git. GitHub should contain code, schema, methodology and small samples only.

## Reproducibility
Every shard uses a repository-ID cursor, SHA-256, row count and checkpoint.
