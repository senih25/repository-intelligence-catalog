# Contributing

Thanks for helping improve Repository Intelligence Catalog.

## Good first contributions
- improve repository metadata validation
- add deterministic ranking/evidence checks
- improve documentation and examples
- propose new curated categories with a reproducible selection rule
- add tests for schema, licensing and freshness checks

## Before opening a pull request
1. Keep public samples metadata-only; do not add repository source code.
2. Do not add secrets, personal data or private machine paths.
3. Revalidate any third-party repository license/status referenced by your change.
4. Run:
   `python tests/smoke.py`
5. Keep claims bounded to evidence in the repository.

## Contribution workflow
- Open an issue for substantial changes.
- Fork/branch from `main`.
- Keep commits focused.
- Include test/evidence notes in the PR description.

## Data-rights boundary
Changes to sample data must follow `DATA_RIGHTS.md`.

By contributing project-authored code/documentation, you agree that your contribution may be distributed under the repository's Apache-2.0 license.
