# Non-Functional Requirements

**Module:** oc-opsdevnz<br />
**Spec Last Updated:** 2026-06-10<br />
**Status:** Draft

---

## NFR-1: Security

### NFR-1.1: Token Protection

**Requirement:** The module MUST NOT log, display, or surface API tokens in plaintext.

**Rationale:**

- OpenCollective API tokens grant write access to fiscal host operations
- Token leakage in logs or error messages is a security incident

**Implementation:**

- Error messages redact the `Api-Key` and `Authorization` header values
- `--log-requests` prints request summaries without header values
- Test suite verifies redaction (`test_http_error_redacts_token`)

### NFR-1.2: Secret Resolution

**Requirement:** The module MUST resolve tokens from 1Password rather than requiring
tokens in environment variables or config files.

**Rationale:**
- Plaintext tokens in `.env` files or shell history are a security risk
- 1Password provides audited, revocable secret access via `op-opsdevnz`

---

## NFR-2: Reliability

### NFR-2.1: Idempotent Operations

**Requirement:** All upsert operations (hosts, collectives, projects) MUST be idempotent.
Running the same YAML file twice MUST produce the same result with no side effects.

**Rationale:**

- YAML-driven infrastructure should follow infrastructure-as-code principles
- Re-running a pipeline should not create duplicate entities or fail on existing ones

### NFR-2.2: Transient Error Handling

**Requirement:** The GraphQL client MUST handle transient failures gracefully with
retry and backoff.

**Rationale:**

- OpenCollective's API may return 5xx errors under load
- 429 rate limiting requires backoff, not immediate failure

---

## NFR-3: Compatibility

### NFR-3.1: Python Version Support

**Requirement:** The module MUST support Python 3.12 through 3.14.

**Rationale:**

- Python 3.12 is the minimum for `|` union type syntax used in the codebase
- Python 3.14 is the current latest; CI should test the full supported range

### NFR-3.2: OpenCollective API Compatibility

**Requirement:** The module MUST work with both the production and staging
OpenCollective GraphQL APIs.

**Rationale:**

- Staging is required for testing collective creation without real financial impact
- Production is the default for actual operations

---

## NFR-4: Code Quality

### NFR-4.1: Linting

**Requirement:** All code MUST pass `ruff check` with no errors.

**Configuration:** `pyproject.toml` enables rules `E`, `F`, `I`, `B` with
line length 100.

### NFR-4.2: Testing

**Requirement:** All public API functions and CLI commands MUST have test coverage.

**Current coverage:** 13 tests covering CLI parser, GraphQL client, and upsert operations.

### NFR-4.3: Dependency Hygiene

**Requirement:** Dependencies MUST be declared with minimum viable version pins in
`pyproject.toml`.

**Core dependencies:**

- `httpx>=0.27.0` — HTTP client with retry support
- `op-opsdevnz>=0.1.0` — 1Password secret resolution
- `PyYAML>=6.0` — YAML parsing for config files

**Dev dependencies:**

- `pytest>=7.4` — Test framework
- `respx>=0.20.0` — HTTP mock for testing GraphQL calls
- `ruff>=0.6.0` — Linting
