# Fiscal Hosting Config Model

**Status:** Draft — opsdev review<br />
**Created:** 2026-06-12<br />
**Author:** opsdev

---

## Problem

SMUNZ is a fiscal host. Collectives can end up under its hosting through different
paths:

1. **SMUNZ creates the collective** via `oc-opsdevnz` (e.g., opsdevnz)
2. **A collective creates itself** via the OpenCollective web UI, then applies to
   be hosted by SMUNZ
3. **A collective transfers** from another fiscal host to SMUNZ

In all three cases, SMUNZ needs to track which collectives it fiscally hosts.
But the degree of control SMUNZ has over each collective's metadata varies.

Currently, the YAML schema only handles case 1 cleanly. There is no way to
represent "we host this collective but we don't control its metadata."

---

## Control Model

| Mode | Who creates | Who controls metadata | SMUNZ controls | YAML `managed_by` |
|------|------------|----------------------|-----------------|-------------------|
| **Managed** | SMUNZ via `oc-opsdevnz` | SMUNZ | name, description, tags, hosting | `smunz` (default) |
| **Hosted** | Collective via OC web UI | Collective | hosting status only | `collective` |
| **Adopted** | Created elsewhere, SMUNZ adopts | Shared — SMUNZ updates hosting, collective controls identity | hosting + some tags | `shared` |

### Managed (`managed_by: smunz`)

SMUNZ created this collective and controls all metadata. The YAML is the source
of truth. Any changes made via the OC web UI will be overwritten on the next
`oc-opsdevnz collectives` run.

Example: opsdevnz, future SMUNZ infrastructure collectives.

### Hosted (`managed_by: collective`)

The collective created itself on OpenCollective and applied to be hosted by
SMUNZ. The YAML entry exists only so SMUNZ can track what it fiscally hosts.
The `oc-opsdevnz` tool should NOT overwrite name, description, or tags — only
verify hosting status.

Example: a future collective like `wellington-devops` that someone else created
and then applied to SMUNZ for fiscal hosting.

### Adopted (`managed_by: shared`)

Transitional or shared-control. SMUNZ manages hosting and some metadata
(tags for categorisation), but the collective controls its own name and
description.

Example: a collective that SMUNZ helped set up but where the founding team
takes over day-to-day management.

---

## Proposed YAML Schema

Add `managed_by` to the collective definition. Defaults to `smunz` for
backward compatibility.

```yaml
# Collectives to create/update and optionally apply to a host (staging)

# Managed: SMUNZ controls all metadata
- name: OpsDev.NZ
  slug: opsdevnz
  managed_by: smunz                   # default, explicit for clarity
  description: Platform engineering and open source infrastructure...
  tags:
    - opsdev
    - infrastructure
    - aotearoa
  host_slug: startmeup-nz
  apply_to_host: true
  host_apply_message: OpsDev.NZ is the infrastructure arm...

# Hosted: Collective controls metadata, SMUNZ only tracks hosting
- slug: future-collective-example
  managed_by: collective              # skip name/desc/tags updates
  host_slug: startmeup-nz
  apply_to_host: false               # already hosted, or they applied via UI
```

### behavioural difference

| `managed_by` | `oc-opsdevnz collectives` behaviour |
|-------------|--------------------------------------|
| `smunz` | Upsert: create if missing, update name/desc/tags if changed |
| `collective` | Verify only: check hosting status, skip metadata updates |
| `shared` | Partial upsert: update tags only, skip name/description |

When `managed_by: collective` and `apply_to_host: false`, `oc-opsdevnz`
performs a read-only check: confirm the collective exists and is hosted by the
specified host. No writes. This is a **drift detection** mode, not a
**reconciliation** mode.

---

## What this means for oc-opsdevnz

### Current behaviour (v0.2.x)

`oc-opsdevnz collectives` always upserts. If a collective exists, it updates
metadata. There is no concept of "don't touch the metadata."

### Required change

- Add `managed_by` field to collective YAML items (optional, defaults to
  `smunz`)
- When `managed_by: collective`, `upsert_collective` should:
  1. Fetch the collective by slug (read)
  2. Verify `host_slug` matches (or apply if `apply_to_host: true`)
  3. Skip all metadata updates (name, description, tags)
- When `managed_by: shared`, `upsert_collective` should:
  1. Fetch the collective by slug (read)
  2. Update tags only
  3. Skip name and description updates

This is a **feature addition**, not a breaking change. Existing YAML files
without `managed_by` continue to work as before (full upsert).

---

## Repository layout

### Current state

- `startmeup.nz/opencollective/` — YAML config + env files (the host's inventory)
- `opsdev.nz/opencollective/` — legacy Python scripts (README says "moved to startmeup.nz")
- Both repos have `env/opencollective-staging.env`

### Proposed

Keep the split. It already makes sense:

| Repo | Contains | Why |
|------|----------|-----|
| `startmeup.nz/opencollective/` | Host, collective, and project YAML for all SMUNZ-hosted collectives | SMUNZ is the fiscal host, this is its inventory |
| `opsdev.nz/opencollective/` | Legacy scripts (deprecated) + reference docs | The tool lives in `oc-opsdevnz`, not here |

When a new collective applies to be hosted by SMUNZ, SMUNZ adds a YAML entry
to `startmeup.nz/opencollective/`. If `managed_by: collective`, the entry is
minimal — just the slug and host reference. This keeps the inventory complete
without SMUNZ needing to control the collective's identity.

### Future: CI pipeline

There is no CI pipeline currently. When one is built, it should:

1. Live in `startmeup.nz` (SMUNZ controls the fiscal host token)
2. Use the same plan/apply pattern as the DNS pipeline:
   - **plan** on MR: `oc-opsdevnz collectives --file ... [--staging]` (dry run)
   - **apply** on merge to main: `oc-opsdevnz collectives --file ... [--staging]`
3. Use `OP_SERVICE_ACCOUNT_TOKEN` for CI authentication

This mirrors the OctoDNS pipeline already in `.gitlab-ci.yml`.

---

## Onboarding workflow for a new collective

1. Collective creates itself on OpenCollective (via web UI)
2. Collective applies to `startmeup-nz` as fiscal host (via UI or `apply_to_host`)
3. SMUNZ evaluates against its onboarding criteria (domain alignment,
   mission match, tooling alignment, operational viability, IP clarity,
   offboarding path)
4. If approved, SMUNZ adds a YAML entry to `startmeup.nz/opencollective/`:

```yaml
- slug: their-collective-slug
  managed_by: collective
  host_slug: startmeup-nz
  apply_to_host: false     # they already applied via UI
```

5. `oc-opsdevnz collectives --file ...` verifies hosting status without
   overwriting metadata
6. The collective appears in SMUNZ's inventory, but controls its own identity

---

## Open questions

1. **Should `managed_by: collective` entries support `apply_to_host: true`?**
   Yes — SMUNZ might need to re-apply hosting if the relationship needs renewal
   or a host transfer. The `apply_to_host` flag still works; `managed_by`
   only controls metadata updates.

2. **What about projects under a `managed_by: collective` collective?**
   Projects under the collective's control should also be `managed_by:
   collective`. If SMUNZ wants to add a project to a hosted collective, that's
   a negotiation, not an automation step. For now, projects under
   `managed_by: collective` collectives should not appear in SMUNZ's project
   YAML unless there's an explicit agreement.

3. **Should we add a `managed_by` field to hosts and projects too?**
   Not currently. Hosts are always SMUNZ-managed (SMUNZ *is* the host).
   Projects inherit from their parent collective's control model. If the
   parent is `managed_by: collective`, its projects are too.