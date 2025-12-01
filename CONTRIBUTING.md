# Contributing

Thanks for helping improve `oc-opsdevnz`! This document mirrors the workflow we use for `op-opsdevnz`, with staging-safe defaults and tests for every change.

## Development Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

We keep tooling in `pyproject.toml`, so editable installs are enough for tests and packaging.

## Common Tasks

| Task      | Command                                     |
|-----------|---------------------------------------------|
| Lint      | `ruff check src tests`                      |
| Tests     | `pytest --color=yes --durations=10`         |
| Build     | `python -m build`                           |

## Pull Requests

1. Create a feature branch.
2. Update/add tests for behavioural changes (HTTP error handling, CLI flows, etc.).
3. Run `ruff` and `pytest` locally (CI will enforce the same).
4. Update documentation (`README.md`, `CHANGELOG.md`, `RELEASING.md`) when behaviour or release steps change.
5. Open a PR and keep CI green.

## Cutting a Release

See [RELEASING.md](RELEASING.md) for the checklist, including TestPyPI → PyPI steps and staging/prod guardrails.
