# Plan and Diff Mode for oc-opsdevnz

**Status:** Draft — feature request<br />
**Created:** 2026-06-12<br />
**Author:** opsdev

---

## Problem

`oc-opsdevnz` currently operates in apply-only mode: `hosts`, `collectives`, and
`projects` subcommands immediately create or update resources on the
OpenCollective API. There is no way to preview what would change before
executing.

This is like running `terraform apply` with no `terraform plan`. For a tool
that manages production infrastructure (OpenCollective collectives, fiscal
hosting), the ability to inspect current state and preview changes is
essential before making them.

---

## Current Behaviour

```
oc-opsdevnz collectives --file staging-collectives.yaml --staging
```

Immediately upserts every collective in the file. Returns JSON showing what
happened, but only after the fact.

---

## Proposed Behaviour

### `show` subcommand (read current state)

Show what exists on OpenCollective for the slugs in the config file.

```
$ oc-opsdevnz show --file staging-collectives.yaml --staging

SLUG              TYPE         EXISTS  HOST              NAME
opsdevnz          COLLECTIVE   no      —                 —
startmeup-nz      ORGANIZATION yes     — (is host)        StartMeUp.NZ
```

For each slug in the YAML, query the API and report:
- Whether the entity exists
- Its type (ORGANIZATION, COLLECTIVE, PROJECT, INDIVIDUAL)
- Its current name, description, tags, host, website
- For collectives: whether it has a fiscal host and which one

### `plan` subcommand (diff without changes)

Compare the YAML desired state against current API state, report what would
change, but make no mutations.

```
$ oc-opsdevnz plan --file staging-collectives.yaml --staging

opsdevnz (COLLECTIVE):
  [CREATE] Would create collective:
    name: "OpsDev.NZ"
    description: "Platform engineering and open source infrastructure..."
    tags: [opsdev, collective, infrastructure, aotearoa, newzealand]
  [APPLY TO HOST] Would apply to startmeup-nz
    message: "OpsDev.NZ is the infrastructure arm of StartMeUp.NZ..."

startmeup-nz (ORGANIZATION):
  [NO CHANGE] Already exists and matches config.

Plan: 1 create, 0 updates, 0 no-ops. Apply with: oc-opsdevnz collectives --file staging-collectives.yaml --staging
```

### Implementation

The `Q_ACCOUNT` GraphQL query already returns all fields we need for comparison:
`id`, `slug`, `name`, `type`, `isHost`, `description`, `longDescription`,
`tags`, `website`, `currency`, `socialLinks`, and `host`.

The existing `_get_account_if_exists()` function already does the read-then-
decide logic internally. Plan mode extracts this into a comparison step:

1. Load YAML items
2. For each item, call `_get_account_if_exists(client, slug)`
3. Compare returned fields against YAML desired state
4. Report differences without calling mutation endpoints

The `managed_by` field (see [fiscal-hosting-config-model.md](./fiscal-hosting-config-model.md))
affects plan output:

| `managed_by` | `plan` shows | `apply` does |
|-------------|-------------|-------------|
| `smunz` | Full diff: name, description, tags, hosting | Full upsert |
| `collective` | Hosting status only; notes metadata is externally controlled | Verify hosting only |
| `shared` | Tags diff; notes name/description are externally controlled | Update tags only |

---

## CLI Interface

```
oc-opsdevnz show [--file ...] [--staging|--prod] [--only SLUG]
oc-opsdevnz plan [--file ...] [--staging|--prod] [--only SLUG]
```

`show` reports current state. `plan` reports desired state vs current state.
Both are read-only — no mutations.

Existing subcommands (`whoami`, `hosts`, `collectives`, `projects`) continue to
work as before (immediate apply). A future `--dry-run` flag could alias to
`plan` for familiarity.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No changes needed (all no-ops) |
| 1 | Error (invalid YAML, API failure) |
| 2 | Changes would be made (plan mode only) |

Exit code 2 for "changes pending" allows scripting:

```bash
oc-opsdevnz plan --file staging-collectives.yaml --staging
if [ $? -eq 2 ]; then
    echo "Changes detected. Review above, then run apply."
    oc-opsdevnz collectives --file staging-collectives.yaml --staging
fi
```

---

## Proposed Work

### Phase 1: `show` subcommand

Add `oc-opsdevnz show` that reads a YAML file and queries each slug, printing a
summary table of current state. This is the foundation for plan mode.

### Phase 2: `plan` subcommand

Add `oc-opsdevnz plan` that diffs YAML desired state against API current state,
printing a detailed change plan without making mutations.

### Phase 3: `managed_by` support

 honour the `managed_by` field in both plan and apply mode, as described in the
 fiscal hosting config model design doc.

---

## Dependencies

- Requires `managed_by` field support in YAML (design doc:
  [fiscal-hosting-config-model.md](./fiscal-hosting-config-model.md))
- The `Q_ACCOUNT` query already returns sufficient fields for comparison
- No new API permissions needed — plan mode only reads