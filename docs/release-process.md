# Release Process

**Module:** oc-opsdevnz
**Status:** Planned — not yet implemented

---

This document will describe the release pipeline for `oc-opsdevnz` once the
GitHub template and CI/CD workflows are backfilled.

## Planned Pipeline

1. **Test** — GitHub Actions workflow on push/PR:
   - Python version matrix (3.12, 3.13, 3.14)
   - Ruff lint, pytest, build verification

2. **Publish to Test PyPI** — On tag push (`v*`):
   - Build package
   - Publish to https://test.pypi.org/ via Trusted Publishing
   - Smoke test: install from Test PyPI, run `--version`

3. **Publish to PyPI** — On success:
   - Build package
   - Publish to https://pypi.org/ via Trusted Publishing

## Current State

- CI workflow exists as `ci.yml` (lint → test → build) — needs splitting
  into `test.yml` and `publish.yml` per the template standard
- SAST scanning not yet configured (bandit, safety, dependabot)

## Reference

- [worklog-opsdevnz publish workflow](https://github.com/startmeup-nz/worklog-opsdevnz/blob/main/.github/workflows/publish.yml)
