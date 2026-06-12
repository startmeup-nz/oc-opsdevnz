# Listing and Inspection Queries for oc-opsdevnz

**Status:** Discovery — not yet implemented<br />
**Created:** 2026-06-12<br />
**Author:** opsdev

---

## Context

`oc-opsdevnz` currently operates in apply-only mode — it creates and updates
resources but cannot list or inspect what already exists. This design note
documents the OpenCollective GraphQL API capabilities for listing and inspection,
which are the foundation for the `show` and `plan` commands described in
[plan-and-diff-mode.md](./plan-and-diff-mode.md).

---

## What `whoami` Does Today

The `whoami` command runs a minimal query:

```graphql
query Account($slug: String!) {
  account(slug: $slug) {
    id
    slug
    name
    type
  }
}
```

This works for any slug — ORGANIZATION, COLLECTIVE, PROJECT, INDIVIDUAL. But it
only returns basic identity fields, not metadata, tags, hosting status, or
children.

`whoami` also does **not** support listing. You can only query one slug at a
time, and you must know the slug beforehand.

---

## GraphQL API Listing Capabilities

### Confirmed (via schema introspection on production API)

The `Host` type exposes these listing fields:

| Field | Returns | Notes |
|-------|---------|-------|
| `hostedAccounts` | Paginated list of accounts hosted by this fiscal host | Use `limit` and `offset` for pagination |
| `hostApplications` | Paginated list of apply-to-host requests | Pending, approved, rejected |
| `totalHostedAccounts` | Integer count | Simple count |
| `childrenAccounts` | Accounts that are children of this account (projects, events) | Available on all Account types |

The `Account` type (parent of all account types) exposes:

| Field | Returns | Notes |
|-------|---------|-------|
| `id`, `slug`, `name`, `type` | Basic identity | Already used in `whoami` |
| `description`, `longDescription`, `tags` | Metadata | Already used in `Q_ACCOUNT` via fragments |
| `isHost` | Boolean | Whether this account is a fiscal host |
| `socialLinks` | List of social links | Website, GitHub, Twitter, etc. |
| `stats` | Financial stats | Balance, etc. |
| `... on AccountWithHost` | `host { slug name }` | The fiscal host, if any |

### Not confirmed (needs auth and staging access)

- Whether `hostedAccounts` returns PROJECT and EVENT types under a COLLECTIVE
- Exact pagination structure (`nodes` vs `edges`, `totalCount` field)
- Whether unauthenticated queries can list all hosted accounts or only public ones

### Ecosyste.ms API (supplementary)

The Ecosyste.ms OpenCollective API (`https://opencollective.ecosyste.ms/api/v1`)
provides read-only listing without authentication:

- `GET /collectives` — all collectives (paginated)
- `GET /collectives/{id}` — single collective by numeric ID
- `GET /collectives/{slug}/projects` — projects under a collective

Rate limit: 5000 req/hour per IP. See the
[related-tools](../related-tools.md) page for details.

---

## Proposed Queries for `show` and `plan`

### 1. Inspect a single account (enhanced whoami)

Replaces the current minimal `whoami` query with `Q_ACCOUNT`, which already
includes description, tags, host, and website:

```graphql
query Account($slug: String!) {
  account(slug: $slug) {
    __typename
    id
    slug
    name
    type
    isHost
    description
    longDescription
    tags
    website
    currency
    ... on AccountWithHost { host { slug name } }
    socialLinks { type url }
    stats { balance { currency } }
  }
}
```

This is **already defined** in `operations.py` as `Q_ACCOUNT`. Just needs a CLI
command that calls it and pretty-prints the result.

### 2. List hosted accounts under a fiscal host

```graphql
query HostedAccounts($slug: String!, $limit: Int!, $offset: Int!) {
  account(slug: $slug) {
    id
    slug
    name
    type
    ... on Host {
      hostedAccounts(limit: $limit, offset: $offset) {
        nodes {
          id
          slug
          name
          type
          __typename
        }
        totalCount
      }
    }
  }
}
```

This lists every collective/project that is fiscally hosted by the given
account. Essential for the `show` command to answer "what collectives does
startmeup-nz host?"

### 3. List projects under a collective

```graphql
query CollectiveProjects($slug: String!, $limit: Int!, $offset: Int!) {
  account(slug: $slug) {
    id
    slug
    name
    type
    ... on AccountWithHost { host { slug name } }
    ... on Account {
      childrenAccounts(limit: $limit, offset: $offset) {
        nodes {
          id
          slug
          name
          type
          __typename
          ... on Project { parent { slug } }
        }
        totalCount
      }
    }
  }
}
```

This lists projects (and events) under a collective. `childrenAccounts` is the
field that returns PROJECT and EVENT type children.

### 4. List all slugs of interest from a config file

Rather than querying each slug individually, the `show` command can:

1. Read the YAML file to get the list of slugs
2. For each slug, query `Q_ACCOUNT` for full state
3. For the host slug, query `hostedAccounts` for hosted collectives
4. For each collective, query `childrenAccounts` for projects

This gives a complete picture of what exists vs what the YAML specifies.

---

## Implementation Priority

| Priority | Command | What It Does | Depends On |
|----------|---------|--------------|------------|
| P0 | `oc-opsdevnz show --file staging-collectives.yaml --staging` | Read each slug from YAML, query API, print current state as a table | New `show` subcommand + `Q_ACCOUNT` |
| P1 | `oc-opsdevnz list-hosted startmeup-nz --staging` | List all collectives hosted by a fiscal host | New `list-hosted` subcommand + `hostedAccounts` query |
| P1 | `oc-opsdevnz list-projects opsdevnz --staging` | List all projects under a collective | New `list-projects` subcommand + `childrenAccounts` query |
| P2 | `oc-opsdevnz plan --file staging-collectives.yaml --staging` | Diff YAML vs API, report changes without applying | P0 + comparison logic |

---

## Open Questions

1. **Does `hostedAccounts` require authentication on staging?** Some GraphQL fields
   require admin-level access. We need to test this with our staging token.

2. **Does `childrenAccounts` return PROJECT-type children?** Confirmed on `Host`
   type via introspection, but need to verify it works for `COLLECTIVE` type
   accounts as well.

3. **Pagination depth.** If startmeup-nz hosts 500 collectives in the future,
   we need pagination support. Start with `limit=100` and paginate.

4. **Ecosyste.ms as a caching layer.** For large-scale listing (e.g., "find all NZ
   collectives"), the Ecosyste.ms API is better suited than querying OC GraphQL
   one slug at a time. Could be used as a discovery tool alongside `show`.