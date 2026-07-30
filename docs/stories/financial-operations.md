# Financial Operations: addFunds & createExpense

**Status:** Draft — design complete, staging-validated, implementation pending
**User:** opsfin (Financial Operations)
**Module:** oc-opsdevnz
**Priority:** P0 — prerequisite for production OC use

---

## Story

**As a financial operator, I want to seed host balances, allocate funds to projects, and create expenses via the CLI so that I can manage collective finances without using the OpenCollective web UI.**

### Context

StartMeUp.NZ is a fiscal host managing four collectives. The `oc-opsdevnz` CLI
already handles entity management (hosts, collectives, projects via YAML-driven
upserts). But financial operations — adding funds to accounts and creating
expenses — are currently only possible through the OpenCollective GraphQL API
directly or the web UI.

Two mutations are needed to close the loop:

- **`addFunds`** — credit a host or project account. Used for host seeding,
  project allocations, and manual adjustments. Idempotent by design (each call
  creates a new transaction; the source of truth is the Beancount ledger).

- **`createExpense`** — submit an expense against a collective for approval,
  processing, and payout.

### Acceptance Criteria

#### `addFunds` subcommand

- [ ] `oc-opsdevnz add-funds --from <slug> --to <slug> --amount <nzd> --description "..."` seeds or allocates funds
- [ ] `--host-fee-percent` flag (defaults to 0 for internal allocations)
- [ ] `--processed-at` flag for backdating (ISO 8601 datetime)
- [ ] `--currency` flag (defaults to NZD)
- [ ] Uses `Decimal` arithmetic internally for dollar→cents conversion (never `float`)
- [ ] Outputs the transaction ID, status, and amount in cents + currency
- [ ] `--staging`/`--prod` environment guardrails
- [ ] Self-referencing `addFunds` (host → host) works for opening balance seeding

#### `createExpense` subcommand

- [ ] `oc-opsdevnz create-expense --account <slug> --description "..." --amount <nzd> --payee <slug>` creates an expense
- [ ] `--type` flag: `INVOICE` (default, preferred for no-file-url friction) or `RECEIPT`
- [ ] `--payout-method` flag: `ACCOUNT_BALANCE` (default, record-only) or `BANK_ACCOUNT`
- [ ] `--items` flag: JSON array of `[{description, amount}]` for multi-line expenses
- [ ] `--incurred-at` flag for backdating
- [ ] Outputs the expense ID, legacy ID, and status
- [ ] `--staging`/`--prod` environment guardrails

### Staging-Validated Patterns

The following patterns were validated against the OC staging API during the July
2026 bootstrap session. All 8 open questions were answered.

| # | Pattern | Result |
|---|---------|--------|
| 1 | Self-referencing `addFunds` for host balance seeding | Works. `startmeup-nz` → `startmeup-nz` with `hostFeePercent: 0` |
| 2 | `addFunds` to project accounts | Works. Host → project allocation with zero host fee |
| 3 | `processedAt` backdating | Accepted. ISO 8601 datetimes in UTC |
| 4 | `editAddedFunds` for corrections | Works. Requires `amount > 0` — $0.01 is the practical minimum |
| 5 | `INVOICE` expense type | Preferred over `RECEIPT`. No per-item file URL requirement |
| 6 | `ACCOUNT_BALANCE` payout method | Record-only. No real money movement. Expense stays PENDING until manually approved/paid |
| 7 | Expense status visibility | APPROVED and PAID are publicly visible; DRAFT and PENDING are not |
| 8 | Pre-allocation requirement | OC requires project balance > 0 before paying expenses. `addFunds` must precede `createExpense` |

### Decimal Arithmetic Requirement

All dollar→cents conversions must use `Decimal` arithmetic:

```python
from decimal import Decimal
cents = int(Decimal("650.00") * 100)  # 65000 — correct
# NEVER: cents = int(650.00 * 100)    # 64999 — rounding error
```

This is non-negotiable for financial accuracy.

### Notes

- **Staging-first:** All `addFunds` and `createExpense` operations should be
  tested against staging before running against production.
- **No delete/undo:** OC does not provide a `deleteAddedFunds` mutation. Use
  `editAddedFunds` to adjust amounts (minimum $0.01).
- **Vendor invite flow preferred:** For expenses paid to external parties, use
  `draftExpenseAndInviteUser` rather than `createExpense` with a pre-existing
  payee slug. This lets the vendor claim the OC account and supply their own
  payout details, keeping PII handling with the vendor.
- **Expense status lifecycle:** DRAFT → PENDING → APPROVED → PAID. Balance
  draws down on PAY, not on CREATE.

### Edge Cases

- What if the from-account has insufficient balance for an allocation?
  (OC enforces this — the mutation will fail with an error)
- What if `processedAt` is in the future? (May be rejected; test on staging)
- What if the payee slug does not exist for `createExpense`?
  (OC will reject; use `draftExpenseAndInviteUser` for unknown vendors)
- What if we need to allocate to a project that doesn't exist yet?
  (Create the project first via `oc-opsdevnz projects`, then allocate)
- What if we duplicate an `addFunds` call? (OC creates a new transaction
  each time; idempotency checks must happen in the caller's ledger)

### Related

- [Functional Requirements](../specs/functional-requirements.md) — existing CLI framework
- [Fiscal Hosting Config Model](../design/fiscal-hosting-config-model.md) — managed/hosted/adopted control
- [Staging Testing Workflow](staging-testing.md) — validation procedure
- [OpenCollective GraphQL API v2](https://docs.opencollective.com/help/developers/api)
