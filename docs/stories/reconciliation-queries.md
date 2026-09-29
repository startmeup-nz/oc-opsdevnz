# Reconciliation Queries: expenses & transactions

**Status:** Draft — query design verified against the deployed OC API (expenses, 2026-09); staging validation pending for the CLI implementation<br />
**User:** opsfin (Financial Operations)<br />
**Module:** oc-opsdevnz<br />
**Priority:** P0 — prerequisite for automated OC ↔ Beancount reconciliation

---

## Story

**As a financial operator, I want to list expenses and transactions from OpenCollective via the CLI so that I can identify their IDs and reconcile them against Beancount entries.**

### Context

The monthly reconciliation runbook has two parts:

1. **ANZ → Beancount** — automated via Akahu fetch + import
2. **OC Alignment** — currently manual web UI

Part 2 is the gap. To automate it, we need to:

1. List OC expenses and transactions from the CLI (this story)
2. Match their `publicId` values against `oc_expense_id` / `oc_transaction_id`
   metadata in Beancount (future reconciliation script)
3. Report any mismatches: expenses in OC without a Beancount entry, or
   Beancount entries referencing missing OC expenses

This story covers step 1: making the data available.

### Acceptance Criteria

#### `expenses` subcommand

- [ ] `oc-opsdevnz expenses <slug>` lists expenses for the given account
- [ ] `--status PAID,APPROVED` filters by expense status (comma-separated, case-insensitive)
- [ ] `--limit 50` controls page size (default 50, max 100)
- [ ] `--offset 0` supports pagination
- [ ] `--since 2026-08-01` and `--until 2026-08-31` filter by date range
- [ ] `--json` outputs machine-readable JSON array
- [ ] Default (no `--json`): human-readable table with ID, status, amount, payee, description, date
- [ ] `--staging` / `--prod` environment guardrails
- [ ] Table output includes `publicId` as the primary reconciliation key
      (`ex_…` / `tx_…`); `legacyId` may be shown alongside for human reference
      only

#### `transactions` subcommand

- [ ] `oc-opsdevnz transactions <slug>` lists transactions for the given account
- [ ] `--kind ADDED_FUNDS,CONTRIBUTION` filters by transaction kind
- [ ] `--limit 50`, `--offset 0` pagination (same as expenses)
- [ ] `--since` / `--until` date range filtering
- [ ] `--json` outputs machine-readable JSON array
- [ ] Default: human-readable table with ID, kind, amount, from/to, description
- [ ] `--staging` / `--prod` environment guardrails

#### Common behaviour

- [ ] Both subcommands handle pagination: output total count and page info
- [ ] `--json` output uses `publicId` as `id` for direct matching against
      `oc_expense_id` / `oc_transaction_id`
- [ ] `--json` output also carries `legacyId` as a separate, clearly display-only
      field — never as the value of `id`
- [ ] Staging-first: test against staging API before using on production
- [ ] Graceful error for accounts that don't exist

### Staging Validation Required

Reconciliation work in September 2026 already verified part of the schema
against the deployed API:

- `expenses(account/host, limit, offset)` works; `publicId` (`ex_…`) is present
  on both single-entity and list queries, and `legacyId` is the numeric ID
  visible in the OC web UI
- `amount` on expenses is a plain Int (cents); the object form is
  `amountV2 { valueInCents currency }`
- Server-side `status: [ExpenseStatus!]` is rejected (the server expects an
  `ExpenseStatusFilter` input, shape unconfirmed); filter client-side
- `dateFrom` filtering verified on `expenses`; a host-wide sweep via
  `expenses(host: $host, hostContext: ALL, dateFrom: $from)` also works

Still to validate against staging before implementing:

| # | Query | What to Confirm |
|---|-------|-----------------|
| 1 | `transactions(limit, offset, kind)` | `TransactionKind` enum values: which are filterable? |
| 2 | Date range filtering | Do `dateTo` (expenses) and `dateFrom`/`dateTo` (transactions) work as `dateFrom` does on expenses? |
| 3 | `order.publicId` on transactions | Does it link back to the originating order? |
| 4 | `expense.publicId` on transactions | Does it link back to the originating expense? |
| 5 | Pagination `totalCount` | Is it accurate? Does it reflect filtered results? |
| 6 | `ExpenseStatusFilter` | Input shape for server-side status filtering (optional; client-side filtering works) |

### Output Examples

#### Table output (default)

```
$ oc-opsdevnz expenses startmeup-nz --staging --status PAID --since 2026-07-01

ID                          Status  Amount      Payee      Description
ex_aUe580n32yQfIOVrV8DV7   PAID    $655.50     sfd-2026   SFD 2026 allocation
ex_1BNohctNGkj5Z6cd3Opah   PAID    $105.50     sfd-2026   SFD 2026 SWAG Box
ex_vgdjBFAOcVvssQ1z0cLWE   PAID    $250.00     opsdevnz   July hosting costs

3 expenses (showing 3 of 3)
```

#### JSON output (for piping)

```
$ oc-opsdevnz expenses startmeup-nz --staging --status PAID --json
[
  {"id": "ex_aUe580n32yQfIOVrV8DV7", "legacyId": 67, "status": "PAID", "amount": 65550, "currency": "NZD", "payee": "sfd-2026", "description": "SFD 2026 allocation", "createdAt": "2026-07-27T..."},
  ...
]
```

### Reconciliation Match Key

The match key between OC and Beancount is the `publicId`:

| OC Field | Beancount Metadata | Example |
|----------|-------------------|---------|
| `expense.publicId` | `oc_expense_id` | `oc_expense_id: "ex_aUe580n32yQfIOVrV8DV7"` |
| `transaction.publicId` | `oc_transaction_id` | `oc_transaction_id: "tx_…"` |

A transaction on OC can also reference its parent via `order.publicId` (for
contributions) or `expense.publicId` (for expenses). The reconciliation script
should consider these parent links when matching.

### Why `publicId` and not `legacyId`

- OpenCollective deprecated `Expense.legacyId` and `Order.legacyId` on
  **2026-02-25**, stating verbatim: *"Legacy ID as returned by API V1. Avoid
  relying on this field as it may be removed in the future."* The stated
  replacement is `publicId`.
- `publicId` is globally unique, so an `oc_expense_id` and an `oc_transaction_id`
  can never collide. `legacyId` is only unique within a type, so Expense 67 and
  Transaction 67 are different things.
- `publicId` is self-describing — the `ex_` / `tx_` prefix identifies the type,
  so a stray metadata key is diagnosable without a lookup.
- It is already our de facto convention: 5 of the 7 live
  `oc_expense_id` / `oc_transaction_id` links in Beancount are `ex_`-form.

`legacyId` remains useful as a **display-only** field: it is the number shown in
the OC web UI, which makes it convenient for a human confirming a match. It must
never be the value used for matching.

### Notes

- **`publicId` is the canonical ID.** The GraphQL `id` field is an opaque
  base64 Relay node ID (`RXhwZW5zZTo…`) intended for machine use only; it is
  not what we store. `publicId` (`ex_…` / `tx_…`) is globally unique, is
  accepted by the mutation inputs, and is what the deprecation notice directs us
  to.
- **`legacyId` is display-only.** Safe to print, useful for eyeballing a match
  against the OC web UI, never to match on.
- **Stale expenses.** An expense marked `PAID` in OC but missing in Beancount
  is a reconciliation gap. The CLI should make this obvious.
- **Pagination is real.** The fiscal host will accumulate hundreds of
  transactions. Always paginate; never assume all results fit in one page.
- **No mutation.** These are read-only queries. No guardrails beyond
  `--staging`/`--prod` token selection are needed.

### Edge Cases

- What if the account slug doesn't exist? → Return a clear error message.
- What if no expenses match the filters? → Return an empty table with "0 expenses."
- What if `--kind` is set to an invalid value? → Validate against known
  `TransactionKind` enum values; report invalid values before querying.
- What if a date range spans multiple pages? → Output should include
  `totalCount` so the caller can paginate.
- What if an expense has been deleted? → Deleted expenses may still appear
  with status `CANCELED` or `REJECTED`; the status filter should handle this.

### Related

- [Listing and Inspection Queries](../design/listing-and-inspection-queries.md) — GraphQL query design
- [Financial Operations](financial-operations.md) — addFunds and createExpense (the write side)
