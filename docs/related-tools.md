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

## Ecosyste.ms: OpenCollective

- **Repo:** `github.com/ecosyste-ms/opencollective`
- **API:** `https://opencollective.ecosyste.ms/api/v1`
- **License:** Code: AGPL-3.0, Data: CC BY-SA 4.0
- **Built with:** Ruby (Rails), PostgreSQL
- **Maintainer:** Andrew Nesbitt (also maintains libraries.io)
- **Part of:** [Ecosyste.ms](https://ecosyste.ms) — tools and open datasets for
  critical digital infrastructure

A public REST API that enriches OpenCollective collectives and their linked
GitHub projects with metadata: repository stats, package dependencies, issue
counts, funding links, and download numbers. It is a **read-only aggregation
layer** — it crawls and indexes public data from OpenCollective and GitHub, then
exposes it through a simple REST API.

**Endpoints** (as of 2026-06):

| Endpoint | Returns |
|----------|---------|
| `GET /collectives` | All collectives (paginated) |
| `GET /collectives/{id}` | Single collective by numeric ID |
| `GET /collectives/{slug}/projects` | Projects under a collective |
| `GET /projects` | All projects (paginated) |
| `GET /projects/{id}` | Single project by numeric ID |
| `GET /projects/lookup?url=...` | Project by repository URL |
| `GET /projects/packages` | Projects with package info |

Each project includes: repo stats, commit counts, issue counts, monthly
downloads, funding links, dependency data, and an Ecosyste.ms "score". Each
collective includes: balance, total donations, total expenses, host, and GitHub
link. Rate limit: 5000 req/hour per IP.

**Overlap with oc-opsdevnz:** Complementary, not competitive. Ecosyste.ms is a
**read-only analytics and discovery** service. Oc-opsdevnz is a **write-capable
lifecycle management** tool (create/update hosts, collectives, projects via the
GraphQL API). They serve different purposes:

| Capability | Ecosyste.ms | oc-opsdevnz |
|-----------|-------------|-------------|
| Read collective data | ✅ REST, no auth | ✅ GraphQL, requires token |
| Create/update collectives | ❌ Read-only | ✅ YAML-driven upsert |
| Project metadata & stats | ✅ Rich (downloads, issues, deps) | ❌ Basic only |
| Funding & financial data | ✅ Aggregate (balance, donations, expenses) | ✅ Direct (via GraphQL) |
| Auth required | ❌ No (public, rate-limited) | ✅ Yes (Personal Token) |
| Environ guardrails | N/A | ✅ Prod/staging separation |
| Use case | Discovery, analytics, reporting | Automation, GitOps, lifecycle |

**When to consider using it:**

- **Dashboard / reporting:** If OpsDev.nz or SMUNZ wants a public-facing
  dashboard showing collective health, funding trends, or project dependency
  data, Ecosyste.ms provides that without hitting the OC GraphQL API or needing
  authentication.
- **Collective discovery:** Finding collectives by category, language, or
  activity level. Useful for SMUNZ's onboarding criteria evaluation (see C1:
  Domain Alignment).
- **Health scoring:** The Ecosyste.ms "score" and monthly download counts could
  enrich SMUNZ's assessment of prospective collectives.

**Reasons not to depend on it:**

- **AGPL-3.0 license** — copyleft. If we embed or link Ecosyste.ms code, AGPL
  obligations apply. Simply consuming the public REST API does not trigger AGPL
  (no code modification), but it must be noted for any future integration.
- **No write operations** — it cannot replace oc-opsdevnz for lifecycle
  management. It supplements, not substitutes.
- **Third-party availability** — it is run by Andrew Nesbitt as part of
  Ecosyste.ms infrastructure. No SLA. If it goes down, our analytics break but
  our automation continues.
- **Data licensing (CC BY-SA 4.0)** — any derivative work from the data must be
  shared under the same license. Fine for analytics, worth noting for anything
  we publish.

---

## How to Add to This Page

When you find a related tool, add an entry with: name, repo, license, what it
does, and how it overlaps with or differs from oc-opsdevnz. This helps us
decide whether to learn from it, integrate with it, or note it as an
alternative.
