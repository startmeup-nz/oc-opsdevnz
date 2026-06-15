# Test Coverage

**Module:** oc-opsdevnz<br />
**Generated:** 2026-06-16<br />
**Command:** `uv run python -m pytest tests/ -v --cov=src/oc_opsdevnz --cov-report=term-missing`

---

## Summary

| Metric | Value |
|--------|-------|
| Total statements | 438 |
| Covered | 366 |
| **Overall coverage** | **84%** |
| Tests | 27 passed, 0 failed |

## Per-File Breakdown

| File | Statements | Missed | Coverage | Gap |
|------|:---:|:---:|:---:|------|
| `operations.py` | 167 | 17 | **90%** | Edge cases in apply-to-host, metadata diff, and warning paths |
| `cli.py` | 129 | 15 | **88%** | `--only` filtering, `cmd_version`, and `main()` error branches |
| `__init__.py` | 8 | 2 | **75%** | `PackageNotFoundError` fallback |
| `oc_client.py` | 127 | 34 | **73%** | Token fallback, staging guard, retry paths, request logging |
| `secrets.py` | 7 | 4 | **43%** | 1Password resolution (hard to unit test) |

## Uncovered Lines

### `cli.py` (lines 47-50, 120, 130-131, 138, 148-149, 156, 222-225, 232)

- `--only` slug filtering in `cmd_hosts`, `cmd_collectives`, and `cmd_projects`
- `cmd_version` body
- `main()` top-level exception handler

### `oc_client.py` (lines 19-24, 64, 73-76, 139, 151-154, 168, 171, 180, 193, 200, 206-207, 209-214, 238-241, 244)

- `_infer_api_url_from_secret_ref` fallback logic
- Token fingerprinting
- `from_secret_ref` factory
- Retry/backoff branches and request logging
- Debug-only error message branches

### `operations.py` (lines 130, 132, 138, 141, 158-159, 188-197, 204, 206, 266, 349, 358)

- Helper edge cases (`_arrays_equal`, `_norm_tags`, `_normalize_url`, `_extract_website`)
- `GraphQLError` not-found detection in `_get_account_if_exists`
- Currency warning path in `upsert_host`
- Drift/warning paths in `upsert_project`

### `secrets.py` (lines 13-20)

- 1Password CLI integration via `op-opsdevnz` requires a running 1Password
  agent. Unit testing this requires either mocking the subprocess call or
  running in an environment with `op` available.

---

## How to Regenerate

```bash
cd public/opsdev.nz/modules/oc-opsdevnz
uv run python -m pytest tests/ -v --cov=src/oc_opsdevnz --cov-report=term-missing
```
