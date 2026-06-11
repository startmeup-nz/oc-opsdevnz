# User Stories

**Module:** oc-opsdevnz<br />
**Status:** Stub

---

User stories capture how different personas interact with `oc-opsdevnz`.

## Personas

| Persona | Role | Primary Use |
|---------|------|-------------|
| **opsdev** | Delivery engineer | Automating collective setup, CI/CD integration |
| **smunz** | Director | Verifying collective configuration, one-off queries |
| **finops** | Financial operations | Reconciling OpenCollective data with ledger |

## Stories

### opsdev (Delivery Engineer)

- [**Staging Testing Workflow**](staging-testing.md) — As an opsdev engineer, I want to test changes on the staging OpenCollective site so that I can verify configuration before applying to production. *Status: Draft*

---

*Stories are written as they are discovered during development and dogfooding.*

### Story Template

```markdown
### As a <persona>, I want to <goal> so that <reason>

**Acceptance Criteria:**

- [ ] Criterion 1
- [ ] Criterion 2

**Notes:**

Additional context, edge cases, related issues.
```

## Related

- [Functional Requirements](../specs/functional-requirements.md)
- [OpsDev.nz persona framework](https://opsdev.nz)
