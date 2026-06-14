# Releasing `oc-opsdevnz`

All releases are automated through GitHub Actions and [Trusted Publishing
(OIDC)](https://docs.pypi.org/trusted-publishers/). No API tokens are stored
or managed — pushing a version tag triggers the pipeline.

## Conventions

| What | Rule |
|------|------|
| Versioning | [Semantic Versioning](https://semver.org) |
| Tag format | `v<version>` (e.g. `v0.2.5`) |
| Branch | `main` only — tags must point at a commit on `main` |
| Auth | Trusted Publishing (OIDC) — no API tokens |

## Prerequisites

- `uv` installed
- Clean `main` branch, CI green
- PyPI Trusted Publisher configured on Test PyPI and PyPI

## Release Workflow

### 1. Prepare

On a branch off `main`:

```bash
# Bump version in pyproject.toml
version = "0.3.0"

# Move changelog entries from [Unreleased] to [0.3.0]
```

### 2. Merge and tag

```bash
git checkout main
git pull origin main
git tag -s v0.3.0 -m "v0.3.0"
git push origin v0.3.0
```

### 3. Watch CI

Pushing the tag fires `.github/workflows/publish.yml`:

| Job | What it does |
|-----|-------------|
| `test-pypi` | Builds wheel, publishes to Test PyPI, installs and runs `oc-opsdevnz version` |
| `pypi` | Runs only if test-pypi passes, publishes to real PyPI |

### 4. Verify

```bash
pip install oc-opsdevnz==0.3.0
oc-opsdevnz version
```

## Dry-run releases

To validate the pipeline without publishing to real PyPI, temporarily comment
out the `pypi` job in `.github/workflows/publish.yml`, tag and push, then
restore it after confirming Test PyPI succeeds.
