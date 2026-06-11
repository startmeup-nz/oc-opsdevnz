# Staging Testing Workflow

**Status:** Draft<br />
**User:** Delivery engineer<br />
**Module:** oc-opsdevnz

---

## As a delivery engineer, I want to test changes on the staging OpenCollective site so that I can verify configuration before applying to production

### Context

OpsDev.nz is launching as an OpenCollective collective. We need to manage collective configuration (hosts, collectives, projects) via YAML files and the `oc-opsdevnz` CLI. Before applying changes to production, we need to verify them against the staging environment.

This is the dogfooding workflow: use oc-opsdevnz to manage the OpsDev.nz collective itself, starting on staging.

### Acceptance Criteria

- [ ] 1Password CLI authenticated on dev environment
- [ ] Staging OC token accessible via `op` (using `OC_SECRET_REF`) or set directly (`OC_TOKEN`)
- [ ] `oc-opsdevnz whoami opsdevnz --staging` returns valid account data
- [ ] Can create/update a test collective on staging via YAML file
- [ ] Can create/update projects under the collective via YAML file
- [ ] Changes on staging are visible in the staging.opencollective.com web UI
- [ ] Process documented for migrating from staging to production

### Workflow

1. **Authenticate:**
   ```bash
   # Option A: Service account token (for automation)
   export OP_SERVICE_ACCOUNT_TOKEN="..."

   # Option B: Interactive sign-in
   op account add --address <team>.1password.com --email <your-email>
   eval $(op signin)
   ```

2. **Set OC token reference:**
   ```bash
   # Option A: Fetch from 1Password at runtime (preferred for automation)
   export OC_SECRET_REF="op://<vault>/<item>/credential"

   # Option B: Set token directly (simpler for testing)
   export OC_TOKEN="<staging-oc-token>"
   ```

3. **Test whoami:**
   ```bash
   oc-opsdevnz whoami opsdevnz --staging
   ```

4. **Apply YAML configuration:**
   ```bash
   # Create/update host (StartMeUp.NZ on staging)
   oc-opsdevnz hosts --file staging-hosts.yaml --staging

   # Create/update collective (OpsDev.NZ on staging)
   oc-opsdevnz collectives --file staging-collectives.yaml --staging

   # Create/update projects
   oc-opsdevnz projects --file staging-projects.yaml --staging
   ```

5. **Verify in web UI:**
   - Log in to https://staging.opencollective.com with your staging account
   - Check that the collective and projects appear correctly
   - Verify tags, descriptions, host application

6. **Migrate to production:**
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

- What if the staging token expires? How do we refresh it?
- What if the collective already exists on staging? (Upsert should handle this)
- What if the host application is rejected on staging? How do we retry?
- What if we need to delete something on staging? (Not currently supported by CLI)

### Related

- [Functional Requirements](../specs/functional-requirements.md)
