# Related Tools

**Module:** oc-opsdevnz

Tools that overlap with or inform what we are building. Some we might learn
from, some might replace parts of our stack, some just prove the pattern works.

---

## OpenCollective MCP Server

- **Repo:** `github.com/theepicsaxguy/opencollective-hetzner-mcp`
- **License:** Apache 2.0
- **Built with:** FastMCP (Python), httpx, Playwright

Wraps the OpenCollective GraphQL API as MCP tools so AI agents can manage
collectives, expenses, transactions, and members programmatically. Originally
built to automate submitting Hetzner cloud invoices as OpenCollective expenses.

Thirteen OpenCollective tools: account queries, expense CRUD, transaction
listing, member management, and a raw GraphQL escape hatch. Six Hetzner
tools for invoice fetching and PDF parsing.

**Overlap with oc-opsdevnz:** Same GraphQL API, same Python + httpx stack.
Different interface (MCP tools vs CLI). Could serve as a reference for an
MCP layer on top of oc-opsdevnz, or as a replacement if it covers our needs.

---

## OpenCollective GraphQL API

- **Docs:** `docs.opencollective.com/help/developers/api`
- **Playground:** `staging-api.opencollective.com/graphql/v2`

The API we wrap. Provides full programmatic access to accounts, collectives,
expenses, transactions, orders, and host management. oc-opsdevnz uses a subset
focused on host/collective/project lifecycle management.

---

## OpenCollective REST API (legacy)

- **Docs:** `docs.opencollective.com/help/developers/api-v1`

The older REST API, partially deprecated. Not used by oc-opsdevnz. GraphQL
is the supported path forward.

---

## oc-opsdevnz (this module)

- **Repo:** `github.com/startmeup-nz/oc-opsdevnz`
- **License:** Apache 2.0

Our tool. CLI + Python library for managing OpenCollective entities as code.
Focused on the collective lifecycle: onboard, support, offboard. YAML-driven,
idempotent, GitOps-friendly. The foundation upon which an MCP server or other
agent interfaces could be built.

---

## How to Add to This Page

When you find a related tool, add an entry with: name, repo, license, what it
does, and how it overlaps with or differs from oc-opsdevnz. This helps us
decide whether to learn from it, integrate with it, or note it as an
alternative.
