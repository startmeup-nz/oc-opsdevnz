# Listing and Inspection Queries for oc-opsdevnz

**Status:** Discovery — not yet implemented<br />
**Created:** 2026-08-11<br />
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

---

## Transaction and Expense Queries (for reconciliation)

These queries support the reconciliation workflow: listing financial
transactions and expenses from OpenCollective so they can be matched against
Beancount entries.

### 5. List expenses for an account

```graphql
query Expenses($slug: String!, $limit: Int!, $offset: Int!, $status: [ExpenseStatus!]) {
  expenses(account: { slug: $slug }, limit: $limit, offset: $offset, status: $status) {
    nodes {
      id legacyId status type description
      amount { valueInCents currency }
      payee { slug name }
      createdAt
    }
    totalCount
  }
}
```

This is the **primary reconciliation query** for the OC → Beancount matching
workflow. Each expense node includes:
- `legacyId` — the numeric ID visible in the OC web UI, used as the
  `oc_expense_id` in Beancount metadata
- `status` — filterable: `PENDING`, `APPROVED`, `PAID`, `REJECTED`, `CANCELED`, `DRAFT`
- `payee.slug` — the account receiving the expense, useful for matching
  against Beancount payee entries

The existing `examples/list_expenses.py` already demonstrates this query.

### 6. List transactions for an account

```graphql
query Transactions($slug: String!, $limit: Int!, $offset: Int!, $kind: TransactionKind) {
  account(slug: $slug) {
    transactions(limit: $limit, offset: $offset, kind: $kind) {
      nodes {
        id legacyId kind type description
        amount { valueInCents currency }
        fromAccount { slug name }
        toAccount { slug name }
        createdAt
        order { id legacyId status }
        expense { id legacyId status }
      }
      totalCount
    }
  }
}
```

Transactions are the broader financial record — they include `ADDED_FUNDS`,
`CONTRIBUTION`, `EXPENSE` entries and more. Key fields for reconciliation:

| Field | Use |
|-------|-----|
| `legacyId` | Maps to `oc_transaction_id` in Beancount metadata |
| `kind` | `ADDED_FUNDS`, `CONTRIBUTION`, `EXPENSE`, `PLATFORM_TIP`, etc. |
| `order.legacyId` | Links back to the originating contribution/order |
| `expense.legacyId` | Links back to the originating expense |
| `fromAccount.slug` / `toAccount.slug` | Source and destination of the entry |

### Reconciliation pipeline design

The target CLI subcommands:

```
oc-opsdevnz expenses <slug>   --staging   --status PAID,APPROVED   --since 2026-08-01   --json
oc-opsdevnz transactions <slug> --staging --kind ADDED_FUNDS      --since 2026-08-01   --json
```

The `--json` flag outputs machine-readable JSON for piping into reconciliation
tooling (e.g., a Beancount matcher script). Without `--json`, output is a
human-readable table.

The reconciliation match key is the `legacyId` — it's the numeric ID visible
in the OC UI and unambiguous. Beancount metadata uses:
- `oc_transaction_id` for transactions (Add Funds, contributions)
- `oc_expense_id` for expenses

A future reconciliation script would:
1. Fetch expenses from OC via `oc-opsdevnz expenses --json`
2. Parse `beancount/ledger.beancount` for entries with `oc_expense_id` metadata
3. Match and report: which OC expenses have no Beancount entry, which Beancount
   entries reference missing OC expenses

### Implementation priority

| Priority | Command | What It Does |
|----------|---------|--------------|
| P0 | `oc-opsdevnz expenses <slug> --staging` | List expenses with status, payee, amounts |
| P1 | `oc-opsdevnz transactions <slug> --staging` | List transactions with kind, from/to accounts |
| P2 | Reconciliation matching script | Cross-reference OC expense IDs ↔ Beancount metadata |

The `expenses` subcommand is P0 because expenses are the primary reconciliation
target — every Beancount expense should link to an OC expense. Transactions
(Add Funds, contributions) are P1 because they're less frequent and already
partially handled by the `addFunds` workflow.

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

5. **`TransactionKind` enum values.** The OC GraphQL schema defines `TransactionKind`
   — staging validation should confirm which values are available and
   filterable. Expected: `ADDED_FUNDS`, `CONTRIBUTION`, `EXPENSE`,
   `PLATFORM_TIP`, `HOST_FEE`, `HOST_FEE_SHARE`, `PAYMENT_PROCESSOR_FEE`.

6. **Time-range filtering.** The `transactions` and `expenses` endpoints both
   accept `dateFrom` and `dateTo` arguments. Staging validation should confirm
   these work as expected for monthly reconciliation windows.