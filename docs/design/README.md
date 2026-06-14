# Design Decisions

**Module:** oc-opsdevnz<br />
**Status:** Stub — populated as decisions are recorded

---

Design decisions for `oc-opsdevnz` follow the ADR (Architecture Decision Record)
format. Each decision captures the context, options considered, outcome, and
rationale.

## Current Decisions

| ID | Title | Status |
|----|-------|--------|
| 001 | [Authentication Strategy](authentication.md) | Draft |
| 002 | [Fiscal Hosting Config Model](fiscal-hosting-config-model.md) | Draft |
| 003 | [Plan and Diff Mode](plan-and-diff-mode.md) | Draft |
| 004 | [Listing and Inspection Queries](listing-and-inspection-queries.md) | Draft |

- **001 Authentication**: Personal Tokens vs OAuth, production readiness requirements, and implementation recommendations.
- **002 Fiscal Hosting Config**: How `managed_by` controls metadata updates when SMUNZ hosts collectives it didn't create. Defines `smunz`, `collective`, and `shared` management modes.
- **003 Plan and Diff Mode**: Adding `show` and `plan` subcommands to oc-opsdevnz for inspecting current state and previewing changes before applying. Like `terraform plan` for OpenCollective.
- **004 Listing and Inspection**: GraphQL query patterns for listing hosted accounts, children, and projects. Foundation for the `show` and `list-hosted` commands.

## ADR Template

```markdown
- ID: [NNN]-{title}
- Title: short title, representative of solved problem and found solution
- Context: Describe the context and problem statement
- Options: Enumerate considered alternatives
- Outcome: Chosen option with justification
- More Information: Additional context, links to related artifacts
```

## Related

- [Functional Requirements](../specs/functional-requirements.md)
- [NFRs](../specs/NFR.md)
- [Related Tools](../related-tools.md)
- [Module README](../index.md)
