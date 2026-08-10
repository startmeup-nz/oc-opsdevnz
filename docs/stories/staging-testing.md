# Staging Testing Workflow

**Status:** Draft<br />
**User:** Operations Development engineer<br />
**Module:** oc-opsdevnz

---

## Story

**As an operations development engineer, I want to test changes on the staging OpenCollective site so that I can verify configuration before applying to production.**

### Context

OpsDev.nz is launching as an OpenCollective collective. We need to manage collective configuration (hosts, collectives, projects) via YAML files and the `oc-opsdevnz` CLI. Before applying changes to production, we verify them against the staging environment.

Staging is treated as user-acceptance testing (UAT): changes are first exercised
against a local mock, then promoted to staging for final validation, and only
lastly applied to production.

### Acceptance Criteria

- [ ] `oc-opsdevnz` commands run successfully against a local mock API first
- [ ] 1Password CLI authenticated on dev environment
- [ ] Staging OC token accessible via `op` (using `OC_SECRET_REF`) or set directly (`OC_TOKEN`)
- [ ] `oc-opsdevnz whoami opsdevnz --staging` returns valid account data
- [ ] Can create/update a test collective on staging via YAML file
- [ ] Can create/update projects under the collective via YAML file
- [ ] Changes on staging are visible in the staging.opencollective.com web UI
- [ ] Process documented for migrating from staging to production

### Workflow

1.) **Validate locally with a mock API:**
   OpsDev.nz maintains a SMUNZ-specific mock server and config for this purpose:
   ```bash
   # From the opsdev.nz repo
   opencollective/mock/run-mock.sh
   ```
   See [Local Mock Development](local-mocking.md) for the full local-first
   workflow.

2.) **Authenticate for staging:**
   ```bash
   # Option A: Service account token (for automation)
   export OP_SERVICE_ACCOUNT_TOKEN="..."

   # Option B: Interactive sign-in
   op account add --address <team>.1password.com --email <your-email>
   eval $(op signin)
   ```

3.) **Set OC token reference:**
   ```bash
   # Option A: Fetch from 1Password at runtime (preferred for automation)
   export OC_SECRET_REF="op://<vault>/<item>/credential"

   # Option B: Set token directly (simpler for testing)
   export OC_TOKEN="<staging-oc-token>"
   ```

4.) **Test whoami:**
   ```bash
   oc-opsdevnz whoami opsdevnz --staging
   ```

5.) **Apply YAML configuration:**
   ```bash
   # Create/update host (StartMeUp.NZ on staging)
   oc-opsdevnz hosts --file staging-hosts.yaml --staging

   # Create/update collective (OpsDev.NZ on staging)
   oc-opsdevnz collectives --file staging-collectives.yaml --staging

   # Create/update projects
   oc-opsdevnz projects --file staging-projects.yaml --staging
   ```

6.) **Verify in web UI:**

- Log in to https://staging.opencollective.com with your staging account
- Check that the collective and projects appear correctly
- Verify tags, descriptions, host application

7.) **Migrate to production:**

- Update YAML files to use production values
- Run commands without `--staging` flag (prod is default)
- Verify on https://opencollective.com

### Notes

- Staging fiscal host: `startmeupnztest2`
- Production fiscal host: TBD (likely `startmeup-nz`)
- Staging requires a separate OpenCollective account
- The `--staging` flag is required for staging; prod is the default
- Environment guardrails prevent accidental prod changes

### Edge Cases

- What if the local mock response shape differs from the real API? Keep the mock
  aligned with the queries in `oc_opsdevnz/operations.py`.
- What if the staging token expires? How do we refresh it?
- What if the collective already exists on staging? (Upsert should handle this)
- What if the host application is rejected on staging? How do we retry?
- What if we need to delete something on staging? (Not currently supported by CLI)

## Staging Validation Results (2026-07-27)

A full bootstrap was validated against the OC staging API. Four throwaway
scripts exercised the core financial operations: preflight cleanup, host
seeding, project allocation, and expense creation. All 8 open questions were
answered.

### Answered Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | How to seed a host with an opening balance? | Self-referencing `addFunds` (host → host). Zero host fee. Works. |
| 2 | What payee slug types does `createExpense` accept? | Any account slug. Tested with project and self-referencing slugs. |
| 3 | Does `ACCOUNT_BALANCE` trigger an actual payout? | Record-only. No real money movement. Expense stays PENDING. |
| 4 | What expense statuses are publicly visible? | APPROVED and PAID are visible. DRAFT and PENDING are not. |
| 5 | Does `addFunds` accept `processedAt` backdating? | Yes. ISO 8601 datetimes in UTC accepted. |
| 6 | Should manual ledger earmarks be removed after OC seeding? | No. Posted governance events stay. OC import must be idempotent. |
| 7 | Can legacy test transactions be reversed? | Yes. `editAddedFunds` works. OC requires `amount > 0` — $0.01 is the practical minimum. |
| 8 | Do project accounts exist on production? | Confirmed via API query. |

### Additional Discoveries

- **`INVOICE` preferred over `RECEIPT`:** `RECEIPT` requires per-item file
  URLs — unnecessary friction for internal expense tracking.
- **Pre-allocation mandatory:** OC requires project balance > 0 before paying
  expenses. `addFunds` must precede `createExpense`.
- **Slug corrections from staging:** OC slugs differ from human-readable
  names (e.g., `opsdevnz` not `opsdev-nz`, `software-freedom-day-2026` not
  `software-freedom-day-wellington-2026`). Always verify slugs via
  `oc-opsdevnz whoami` or the GraphQL explorer before scripting.
- **Balance with pending:** Use `stats.balanceWithPending` to see the
  balance including pending expenses. Useful for reconciliation checks.
- **Decimal arithmetic:** Dollar→cents conversion must use `Decimal`, never
  `float`. See [Financial Operations](financial-operations.md).

### Related

- [Financial Operations](financial-operations.md) — addFunds and createExpense spec
- [Functional Requirements](../specs/functional-requirements.md)
- [Local Mock Development](local-mocking.md)
