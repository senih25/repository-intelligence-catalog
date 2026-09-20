# Repository Intelligence Catalog

**Evidence-backed repository discovery and reuse decisions for developers and AI coding agents.**

Repository Intelligence Catalog turns repository discovery into a controlled, auditable workflow:

**Need → Search → Evidence → REUSE / ADAPT / REFERENCE / AVOID**

Instead of treating stars, forks, or a public repository URL as proof of quality, the project separates cheap discovery from explicit reuse gates such as licensing, archive state, maintenance, security/dependency review, and project fit.

## What this repository provides

The public v0.1.0 package contains:

- a resumable GitHub public-repository metadata harvester;
- checkpointed, compressed JSONL shards with SHA-256 receipts;
- a bounded local SQLite + FTS5 hot index;
- a query CLI with archived/license filters;
- a JSON Schema for repository records;
- a reproducible 15-repository metadata demo across five developer-tool categories;
- smoke checks for sample/schema integrity;
- methodology, security, attribution, licensing, data-rights, release, and contribution guidance.

The private canonical corpus and third-party repository source code are **not** included.

## Architecture

```text
GitHub public repository metadata
        ↓
compact repository records
        ↓
checkpoint + gzip JSONL shards + SHA-256 queue
        ↓
bounded SQLite / FTS5 hot index
        ↓
CLI retrieval and deterministic filters
        ↓
evidence review
        ↓
REUSE / ADAPT / REFERENCE / AVOID
```

The inventory grain is one GitHub repository ID. Bulk discovery is intentionally separated from expensive enrichment and final reuse decisions.

## Core components

| Component | Purpose |
|---|---|
| `src/harvest_public_repos.py` | Resumable metadata collection from the GitHub public repositories endpoint, with rate-limit handling, checkpoints, chunking, local quota guards, and SHA-256 queue receipts. |
| `src/build_hot_index.py` | Builds a bounded SQLite database and FTS5 index from local/cloud JSONL shards. |
| `src/search_hot_index.py` | Searches the hot index with FTS ranking, archive filtering, optional license requirements, and bounded result limits. |
| `schema/repository.schema.json` | Defines the public repository-intelligence record contract. |
| `sample/curated_repositories.csv` | Auditable 15-repository demo dataset. |
| `tests/smoke.py` | Verifies row count, required schema fields, unique repository IDs, GitHub URLs, and archived flags. |
| `METHODOLOGY.md` | Documents the two-stage discovery/enrichment model and evidence rules. |
| `DATASET_CARD.md` / `DATA_RIGHTS.md` | Define dataset scope, intended use, limitations, and third-party rights boundaries. |

## Quick start

The current implementation uses Python's standard library for the included CLI workflow.

### 1. Validate the public sample

```bash
python tests/smoke.py
```

Expected result:

```json
{"status":"PASS","rows":15,"unique_repo_ids":15}
```

### 2. Review runtime configuration

Check `config/settings.json` before harvesting. An optional GitHub token is read from the environment variable configured by `token_env`; secrets should not be written into repository files.

### 3. Run a bounded harvest

```bash
python src/harvest_public_repos.py --max-repos 1000 --fresh
```

The harvester writes resumable state and compressed shards under the local staging area. Unlimited harvesting requires the explicit `--full` flag and remains subject to configured quota guards and GitHub rate limits.

### 4. Build the hot index

```bash
python src/build_hot_index.py --reset
```

### 5. Search for candidates

```bash
python src/search_hot_index.py "mcp" --limit 20 --license-required
```

Archived repositories are excluded by default. Use `--include-archived` only when that is intentional.

## Reuse discipline

A public GitHub repository is not automatically reusable open-source software. Before integrating a candidate, revalidate:

1. current license and intended-use compatibility;
2. archived/deprecated status;
3. maintenance and release activity;
4. dependency and supply-chain risk;
5. relevant security advisories;
6. fit with the active project architecture;
7. a minimal smoke test.

Stars and forks are **discovery signals**, not proof of security, maintenance quality, or project fit.

## Verified evidence boundary

The validated engineering pilot has enumerated **1,200 repositories** with checkpoint/resume and Drive-backed cold storage.

That 1,200-row pilot is **not** a claim that the complete GitHub repository universe has been analyzed.

The public demo contains **15 selected repositories across five categories** and is intentionally small enough to inspect and reproduce. The public sample contains repository-level technical metadata, not repository source code or contributor profiles.

## Public dataset and notebook

- Kaggle dataset: https://www.kaggle.com/datasets/senihbayankulu/repository-intelligence-catalog
- Kaggle notebook: https://www.kaggle.com/code/senihbayankulu/repository-intelligence-15-repo-demo

The Kaggle package is a curated demonstration surface for retrieval, filtering, and repository-intelligence experiments; it is not a statistically representative sample of GitHub.

## Licensing and data rights

Original project code and documentation are licensed under **Apache-2.0**.

The curated metadata sample is governed by [DATA_RIGHTS.md](DATA_RIGHTS.md). This repository does not grant rights to third-party repositories, source code, names, trademarks, or other underlying content.

See also:

- [LICENSE](LICENSE)
- [NOTICE.md](NOTICE.md)
- [TERMS_AND_ATTRIBUTION.md](TERMS_AND_ATTRIBUTION.md)
- [DATASET_CARD.md](DATASET_CARD.md)
- [METHODOLOGY.md](METHODOLOGY.md)
- [SECURITY.md](SECURITY.md)

## Roadmap

The next planned layers are documented in [ROADMAP.md](ROADMAP.md):

- automated CI for schema/smoke checks;
- retrieval-quality benchmarks and deterministic candidate scoring;
- freshness, archive, and license gates;
- exportable evidence receipts;
- provider-neutral MCP/read integration;
- reproducible agent-facing project-context retrieval.

## Community

- [Contributing](CONTRIBUTING.md)
- [v0.2 retrieval benchmark issue](https://github.com/senih25/repository-intelligence-catalog/issues/1)
- [Good first issue](https://github.com/senih25/repository-intelligence-catalog/issues/2)
- [v0.1.0 release](https://github.com/senih25/repository-intelligence-catalog/releases/tag/v0.1.0)

## Status

**v0.1.0 public release.**

The GitHub repository and curated Kaggle dataset are public. Claims remain bounded to dated evidence and reproducible sample artifacts.

Repository Intelligence Catalog is an independent project and is not affiliated with or endorsed by GitHub.
