# Test Coverage

**Module:** oc-opsdevnz<br />
**Generated:** 2026-06-10<br />
**Command:** `uv run python -m pytest tests/ -v --cov=src/oc_opsdevnz --cov-report=term-missing`

---

## Summary

| Metric | Value |
|--------|-------|
| Total statements | 420 |
| Covered | 305 |
| **Overall coverage** | **73%** |
| Tests | 13 passed, 0 failed |

## Per-File Breakdown

| File | Statements | Missed | Coverage | Gap |
|------|:---:|:---:|:---:|------|
| `operations.py` | 167 | 21 | **87%** | Edge cases in apply-to-host and error paths |
| `__init__.py` | 8 | 2 | **75%** | `PackageNotFoundError` fallback |
| `oc_client.py` | 127 | 34 | **73%** | Token fallback, staging guard, retry paths |
| `cli.py` | 111 | 54 | **51%** | Command execution (parser only tested) |
| `secrets.py` | 7 | 4 | **43%** | 1Password resolution (hard to unit test) |

## Uncovered Lines

### `cli.py` (lines 42-192)

CLI command functions (`cmd_whoami`, `cmd_hosts`, `cmd_collectives`,
`cmd_projects`) and `main()` error handler are not exercised through the
full execution path. Tests validate argument parsing but not live CLI
execution against mocked GraphQL endpoints.

### `oc_client.py` (lines 19-244)

Token resolution fallback chain, staging environment guard, retry/backoff
logic, and request-logging branches are not fully exercised.

### `operations.py` (lines 125-358)

Edge cases: apply-to-host when already hosted, metadata diff detection,
and warning accumulation paths.

### `secrets.py` (lines 13-20)

1Password CLI integration via `op-opsdevnz` requires a running 1Password
agent. Unit testing this requires either mocking the subprocess call or
running in an environment with `op` available.

---

## How to Regenerate

```bash
cd public/opsdev.nz/modules/oc-opsdevnz
uv run python -m pytest tests/ -v --cov=src/oc_opsdevnz --cov-report=term-missing
```
