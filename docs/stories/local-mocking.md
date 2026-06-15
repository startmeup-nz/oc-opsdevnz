# Local Mock Development

**Status:** Draft<br />
**User:** Operations Development engineer<br />
**Module:** oc-opsdevnz

---

## Story

**As an Operations Development engineer, I want to develop and test `oc-opsdevnz`
against a local mock OpenCollective API so that I can iterate on the tool without
making changes to the official staging or production environments that
OpenCollective manages.**

### Context

`oc-opsdevnz` targets the OpenCollective GraphQL API. The public staging and
production endpoints are shared, managed environments. Running every development
build or test against them risks creating noise, hitting rate limits, or leaving
behind test data. A local mock lets the team validate YAML shapes, CLI wiring,
mutation payloads, and error handling before any request reaches a shared
environment.

### Acceptance Criteria

- [ ] A developer can point the CLI at a local mock endpoint with `--api-url`.
- [ ] A local mock server responds to the queries and mutations used by
      `whoami`, `hosts`, `collectives`, and `projects`.
- [ ] Unit tests continue to use `respx` and run without network access.
- [ ] The local → staging → production workflow is documented.
- [ ] No OpenCollective-managed credentials are required for local-only work.

### Workflow

1.) **Start a local mock server.** Any HTTP server that responds to GraphQL
   `POST /graphql/v2` and returns the expected query/mutation shapes will work.
   See the OpsDev.nz repository for a concrete example that mirrors the
   StartMeUp.NZ fiscal host setup.

2.) **Run CLI commands against the mock:**
   ```bash
   export OC_TOKEN="mock-token"
   oc-opsdevnz whoami example-collective \
       --api-url http://localhost:8765/graphql/v2 --token mock-token
   oc-opsdevnz hosts --file hosts.yaml \
       --api-url http://localhost:8765/graphql/v2 --token mock-token
   oc-opsdevnz collectives --file collectives.yaml \
       --api-url http://localhost:8765/graphql/v2 --token mock-token
   oc-opsdevnz projects --file projects.yaml \
       --api-url http://localhost:8765/graphql/v2 --token mock-token
   ```

3.) **Iterate on code or YAML:**

- Edit the module or configuration.
- Re-run against the mock to verify request shapes and response handling.
- Add failing cases to the mock to exercise error paths.

4.) **Promote to staging (UAT):**

- Once local tests pass, run the same commands against staging with
     `--staging` and a real staging token.
- Verify changes in the staging web UI.

5.) **Promote to production:**

- After staging sign-off, run without `--staging` using a production token.

### Notes

- The mock server is intentionally simple. It validates CLI wiring and request
  shape, not OpenCollective business logic such as host-approval workflows.
- For headless automation and CI, use `respx` fixtures in `tests/` rather than
  a standalone mock server.
- Keep staging and production tokens out of local mock commands by using
  `--token` explicitly.

### Concrete Example

OpsDev.nz maintains a SMUNZ-specific mock server and YAML files for local
testing in its own repository:

- `opsdev.nz/opencollective/mock/mock_server.py`
- `opsdev.nz/opencollective/mock/run-mock.sh`
- `opsdev.nz/opencollective/mock/mock-*.yaml`

### Related

- [Functional Requirements](../specs/functional-requirements.md)
- [Staging Testing Workflow](staging-testing.md)
