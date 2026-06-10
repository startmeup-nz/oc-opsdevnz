# Functional Requirements

**Module:** oc-opsdevnz<br />
**Module Version:** see `pyproject.toml`

---

## FR-1: GraphQL Client

The module MUST provide an httpx-based GraphQL client for the OpenCollective API.

### FR-1.1: Request Execution

- **FR-1.1.1**: Client MUST accept a GraphQL query string and variables dict, returning the
  `data` field from the JSON response
- **FR-1.1.2**: Client MUST raise `GraphQLError` when the response contains an `errors` array
- **FR-1.1.3**: Client MUST raise `HTTPRequestError` on non-2xx HTTP responses
- **FR-1.1.4**: Client MUST raise `TransportError` on network-level failures (connection refused,
  timeout, DNS resolution)

### FR-1.2: Retry and Backoff

- **FR-1.2.1**: Client MUST retry on transient HTTP errors (5xx, 429) with exponential backoff
- **FR-1.2.2**: Client MUST NOT retry on client errors (4xx, excluding 429)

### FR-1.3: Error Message Redaction

- **FR-1.3.1**: Error messages MUST NOT expose the API token in plaintext
- **FR-1.3.2**: When a request fails and the Authorization header contains a token, the error
  message MUST redact the token value before surfacing to the user

---

## FR-2: Token Resolution

The module MUST resolve OpenCollective API tokens from 1Password via `op-opsdevnz`.

### FR-2.1: Resolution Chain

- **FR-2.1.1**: If `OC_SECRET_REF` environment variable is set, the client MUST resolve the token
  from the 1Password secret reference using `op-opsdevnz`
- **FR-2.1.2**: If `OC_TOKEN` environment variable is set and `OC_SECRET_REF` is not, the client
  MUST use `OC_TOKEN` directly as the API token
- **FR-2.1.3**: If neither `OC_SECRET_REF` nor `OC_TOKEN` is set, and no explicit `--token` is
  provided, the client MUST raise a clear error indicating what environment variables are expected

### FR-2.2: Token Override

- **FR-2.2.1**: CLI MUST accept a `--token` flag to override environment-based token resolution
- **FR-2.2.2**: Python API MUST accept a `token` parameter to the `OpenCollectiveClient` constructor

### FR-2.3: Authentication Mode

- **FR-2.3.1**: Client MUST support `personal` (Personal-Token) authentication via
  `Api-Key` header
- **FR-2.3.2**: Client MUST support `oauth` (OAuth bearer) authentication via
  `Authorization: Bearer` header

---

## FR-3: Environment Guardrails

The module MUST enforce safe defaults and explicit opt-in for non-production environments.

### FR-3.1: Production Default

- **FR-3.1.1**: `OpenCollectiveClient()` with no arguments MUST target the production
  OpenCollective API (`https://api.opencollective.com/graphql/v2`)
- **FR-3.1.2**: `OpenCollectiveClient.for_prod()` MUST explicitly target production

### FR-3.2: Staging Opt-In

- **FR-3.2.1**: `OpenCollectiveClient.for_staging()` MUST target the staging API
  (`https://staging-api.opencollective.com/graphql/v2`)
- **FR-3.2.2**: CLI MUST accept `--staging` and `--test` (alias) flags to target staging
- **FR-3.2.3**: CLI MUST accept `--prod` for explicitness, though production is the default

### FR-3.3: Custom Endpoint

- **FR-3.3.1**: Client MUST accept a `--api-url` / `api_url` parameter to override the
  GraphQL endpoint entirely

---

## FR-4: CLI Interface

The module MUST provide a command-line interface with subcommands for common
OpenCollective operations.

### FR-4.1: Subcommands

- **FR-4.1.1**: `whoami <slug>` — MUST fetch and display account/collective metadata
  (id, slug, name, type)
- **FR-4.1.2**: `hosts` — MUST read a YAML/JSON file of host definitions and upsert
  each host organisation via the GraphQL API
- **FR-4.1.3**: `collectives` — MUST read a YAML/JSON file of collective definitions,
  create or update each collective, and optionally apply it to a fiscal host
- **FR-4.1.4**: `projects` — MUST read a YAML/JSON file of project definitions and
  upsert each project under its parent collective
- **FR-4.1.5**: `version` — MUST print the installed package version

### FR-4.2: Common Options

All subcommands MUST accept:

- `--prod` / `--staging` / `--test` — environment selection
- `--api-url` — custom GraphQL endpoint
- `--token` — explicit API token
- `--auth-mode` — `personal` (default) or `oauth`
- `--log-requests` — print request summaries for debugging

### FR-4.3: File Input

- **FR-4.3.1**: `hosts`, `collectives`, and `projects` subcommands MUST accept a `--file`
  argument pointing to a YAML or JSON file containing an array of item definitions
- **FR-4.3.2**: A `--config` alias MUST be accepted for `--file` to support
  environment-named configs (e.g., `staging-collectives.yaml`)
- **FR-4.3.3**: An `--only <slug>` flag MUST filter processing to a single item by slug

### FR-4.4: Output

- **FR-4.4.1**: Operations MUST output JSON to stdout indicating created/updated/applied status
- **FR-4.4.2**: Errors MUST be printed to stderr with a clear message

---

## FR-5: YAML-Driven Upsert Operations

The module MUST provide idempotent upsert semantics for hosts, collectives, and projects.

### FR-5.1: Upsert Semantics

- **FR-5.1.1**: If an entity with the given slug already exists, the operation MUST update
  its metadata (name, description, tags) if changed, and MUST skip creation
- **FR-5.1.2**: If an entity does not exist, the operation MUST create it
- **FR-5.1.3**: The operation MUST return an `UpsertResult` indicating whether the entity
  was created, updated, or unchanged

### FR-5.2: Host Definition

A host YAML item MUST support:

- `name` — display name
- `slug` — unique identifier
- `description` — optional description
- `website` — optional URL
- `currency` — ISO 4217 currency code (e.g., `nzd`)
- `tags` — list of string tags

### FR-5.3: Collective Definition

A collective YAML item MUST support:

- `name` — display name
- `slug` — unique identifier
- `description` — optional description
- `tags` — list of string tags
- `host_slug` / `hostSlug` — fiscal host to apply to
- `apply_to_host` / `applyToHost` — boolean, whether to apply to the host
- `host_apply_message` / `hostApplyMessage` — message sent with the apply-to-host request

### FR-5.4: Project Definition

A project YAML item MUST support:

- `name` — display name
- `slug` — unique identifier
- `parent_slug` / `parentSlug` — parent collective slug
- `description` — optional description
- `tags` — list of string tags

### FR-5.5: Apply-to-Host Flow

- **FR-5.5.1**: When `apply_to_host` is true, the operation MUST verify the host exists
  and is a valid fiscal host before creating the collective
- **FR-5.5.2**: If the collective is already hosted by the specified host, the operation
  MUST skip the apply step
- **FR-5.5.3**: If the collective is hosted by a different host, the operation MUST
  apply it to the specified host with the provided message

### FR-5.6: Input Validation

- **FR-5.6.1**: The input file MUST contain a top-level YAML/JSON array
- **FR-5.6.2**: If the file does not contain an array, the operation MUST exit with
  a clear error
- **FR-5.6.3**: The `load_items()` function MUST accept both `.yaml`/`.yml` and `.json` files

---

## Verification

| Requirement ID | Verification Method | Test/Artifact Link | Status |
|----------------|---------------------|--------------------|--------|
| FR-1.1 | test | `tests/test_client.py::test_prod_guard` | Passed |
| FR-1.2 | test | `tests/test_client.py::test_http_error_redacts_token` | Passed |
| FR-1.3 | test | `tests/test_client.py::test_graphql_error_surfaces_message` | Passed |
| FR-4.1 | test | `tests/test_cli_parser.py` | Passed |
| FR-5.1 | test | `tests/test_operations.py::test_upsert_host_creates_and_updates` | Passed |
| FR-5.2 | test | `tests/test_operations.py::test_upsert_host_no_update_when_same` | Passed |
| FR-5.3 | test | `tests/test_operations.py::test_collective_create_and_apply_to_host` | Passed |
| FR-5.4 | test | `tests/test_operations.py::test_project_create_and_update` | Passed |
| FR-5.6 | test | `tests/test_operations.py::test_load_items_requires_list` | Passed |
