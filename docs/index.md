# oc-opsdevnz

OpenCollective API client and CLI for OpsDev.nz. Resolves tokens from 1Password
via `op-opsdevnz`. Supports both production and staging OpenCollective environments.

- **Status:** Development
- **License:** Apache 2.0
- **Python:** 3.12+

## Overview

StartMeUp.NZ operates as a fiscal host for early-stage collectives. Each
collective has a lifecycle: onboarding, a support period (typically one year),
and offboarding. Doing this by clicking through the OpenCollective web UI
for every host, collective, and project does not scale.

`oc-opsdevnz` lets us manage our presence on OpenCollective as code.
Collectives and their configuration live in YAML files. The CLI applies them
idempotently via the GraphQL API. This means:

- **Repeatable onboarding:** a new collective is a YAML file and one command
- **GitOps workflow:** collective state is versioned, reviewed, and auditable
- **Agent-friendly:** AI assistants can propose collective changes via YAML
  without needing access to the OpenCollective web UI
- **Low overhead:** automation keeps operating costs down so we do not need
  to pass fees on to the collectives we support

The final shape of this tool is still evolving. The direction is clear: make
collective lifecycle management easy, automated, and manageable via Git.

It wraps the OpenCollective GraphQL API with:

- httpx-based GraphQL client with retries, backoff, and redacted error messages
- Token resolution from 1Password via `op-opsdevnz` (`OC_SECRET_REF` / `OC_TOKEN`)
- Environment guardrails: prod by default, explicit `--staging`/`--test` for staging
- CLI helpers for whoami, host upserts, collective creation, and project management

## Quick Start

```bash
# Install
uv pip install oc-opsdevnz op-opsdevnz

# Set your token reference
export OC_SECRET_REF="op://startmeup.nz/api.opencollective.com/credential"

# Fetch an account
oc-opsdevnz whoami opsdevnz

# Create collectives from YAML
oc-opsdevnz collectives --file collectives.yaml --staging
```

## CLI Commands

| Command | Purpose |
|---------|---------|
| `whoami <slug>` | Fetch account/collective metadata by slug |
| `hosts` | Create/update host organisations from YAML |
| `collectives` | Create/update collectives and apply to a host |
| `projects` | Create/update projects under a parent collective |
| `version` | Print installed package version |

All commands accept `--staging`/`--test` to target the staging API, or
`--api-url` to override the GraphQL endpoint explicitly.

## Python API

```python
from oc_opsdevnz import OpenCollectiveClient, load_items, upsert_collective, upsert_host
from pathlib import Path

client = OpenCollectiveClient.for_staging()

# Upsert hosts from a YAML file
for host in load_items(Path("hosts.yaml")):
    upsert_host(client, host)

# Create a collective and apply to host
for coll in load_items(Path("collectives.yaml")):
    upsert_collective(client, coll)
```

## Documentation

- **[Specifications](specs/)** — Functional and non-functional requirements
- **[Design Decisions](design/README.md)** — Architecture choices and rationale
- **[User Stories](stories/README.md)** — Persona-driven narratives
- **[Related Tools](related-tools.md)** — Similar tools, alternatives, and references

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run python -m pytest tests/ -v

# Lint
uv run ruff check src tests

# Serve documentation
uv run zensical serve
```

## Related

- [OpsDev.nz Collective](https://opsdev.nz) — Parent project
- [OpenCollective GraphQL API](https://docs.opencollective.com/help/developers/api)
- [op-opsdevnz](https://pypi.org/project/op-opsdevnz/) — 1Password secret resolution
