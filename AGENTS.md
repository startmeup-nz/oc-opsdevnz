# Agents.md — oc-opsdevnz

**Audience:** Contributors and AI assistants working on the oc-opsdevnz module.

## IMPORTANT: No Autonomous Commits

AI assistants must NOT commit changes to this repository. Always stage changes
and describe what was done, then wait for human review and confirmation before
committing. This ensures all changes have human oversight.

## Module Scope

oc-opsdevnz is an OpenCollective API client and CLI for OpsDev.nz. It provides:

- httpx-based GraphQL client with retries, backoff, and redacted errors
- Token resolution from 1Password via `op-opsdevnz`
- CLI subcommands: `whoami`, `hosts`, `collectives`, `projects`, `version`
- YAML-driven idempotent upsert operations for hosts, collectives, and projects
- Prod/staging environment guardrails

## Zensical Documentation Server

**AI assistants should NOT start the Zensical dev server.** The human developer
controls when and where `zensical serve` runs — it binds a port and stays
running, which is a human-level decision.

AI assistants MAY:
- Run `uv run zensical build` to verify docs render without errors
- Edit `zensical.toml` configuration
- Edit markdown files under `docs/`

## Development Workflow

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests (13 tests, all passing)
uv run python -m pytest tests/ -v

# Lint
uv run ruff check src tests

# Build docs (verify render, no errors)
uv run zensical build
```

## Testing

Tests use `respx` to mock httpx responses — no real API calls are made.

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run a specific test file
uv run python -m pytest tests/test_operations.py -v
```

## Versioning

- **0.2.x** — Current development, API may shift as module matures
- **1.0.0** — Stable release, semantic versioning enforced

## Current Focus

- Backfill GitHub template (test.yml, publish.yml, sast.yml, dependabot.yml)
- Match the `practice-template-opsdevnz` standard
- Create spec and documentation (in progress — June 2026)
- Dogfood: use this module to set up OpsDev.nz as an OpenCollective collective

## GraphQL API Notes

- Production endpoint: `https://api.opencollective.com/graphql/v2`
- Staging endpoint: `https://staging-api.opencollective.com/graphql/v2`
- Staging requires a separate account and API token
- The staging fiscal host is `startmeupnztest2`; production is TBD

## Related

- [OpenCollective GraphQL API docs](https://docs.opencollective.com/help/developers/api)
- [op-opsdevnz](https://github.com/startmeup-nz/op-opsdevnz) — 1Password secret resolution
- [Module template repo](https://github.com/startmeup-nz/practice-template-opsdevnz)
