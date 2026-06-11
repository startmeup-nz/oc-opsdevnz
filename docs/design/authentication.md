# Authentication Design for oc-opsdevnz

**Status:** Draft<br />
**Created:** 2026-06-11<br />
**Author:** opsdev

---

## Problem Statement

oc-opsdevnz needs to authenticate with the OpenCollective API to manage collectives, hosts, and projects. We need to choose an authentication strategy that:

1. Works for automation (CI/CD, scheduled tasks)
2. Works for local development
3. Is secure and maintainable
4. Supports both staging and production environments

---

## Current Architecture

### Secret Resolution (op-opsdevnz)

The `op-opsdevnz` module resolves secrets from 1Password.

It accepts `op://` references (e.g., `op://vault/item/field`)

Supports two resolution methods:

1. **SDK**: Uses `OP_SERVICE_ACCOUNT_TOKEN` environment variable
2. **CLI**: Falls back to `op` binary if installed and authenticated

And returns the secret value plus metadata about which resolver was used.

### OpenCollective Client (oc-opsdevnz)

The `oc-opsdevnz` module uses op-opsdevnz to obtain the OpenCollective API token:

- `OC_SECRET_REF` environment variable points to 1Password reference
- `OC_TOKEN` environment variable can override for local testing
- Uses `Personal-Token` HTTP header for API authentication

---

## OpenCollective Authentication Options

OpenCollective supports two authentication methods for API access:

### 1. Personal Tokens

**Description:** User-scoped API tokens tied to an OpenCollective account.

**Characteristics:**

- Tied to a specific user account
- Can be scoped (email, account, expenses, orders, transactions, etc.)
- Can have expiration dates
- Simple to use: pass token in `Personal-Token` HTTP header
- No user interaction required for automation

**Use Cases:**

- Automation and scripting
- Single-user tools
- CI/CD pipelines
- Integration with external services

**Limitations:**

- Tied to a user account (if user leaves, token becomes invalid)
- No built-in token refresh mechanism
- Manual rotation required

### 2. OAuth (Authorization Code Flow)

**Description:** Standard OAuth 2.0 authorization code flow for multi-user applications.

**Characteristics:**

- Requires user interaction (redirect-based authorization)
- Scoped access (same scopes as Personal Tokens)
- Access tokens expire and require refresh
- Can act on behalf of multiple users
- Supports 2FA with special configuration

**Use Cases:**

- Multi-user SaaS applications
- Web applications where users authenticate via OpenCollective
- Applications that need to act on behalf of different users

**Limitations:**

- Requires user interaction (not suitable for headless automation)
- More complex to implement (redirect flow, token refresh)
- Requires registering an OAuth application

### 3. OpenID Connect (OIDC)

**Not supported by OpenCollective.** OIDC is for identity/authentication (proving who you are), not API authorization (what you can do). OpenCollective uses Personal Tokens or OAuth for API access.

---

## Decision: Personal Tokens

**Decision:** Use Personal Tokens for oc-opsdevnz authentication.

**Rationale:**

1. **Automation-first use case:** We're automating tasks for our own collective (OpsDev.nz), not building a multi-user application.

2. **No user interaction required:** Personal Tokens work in headless environments (CI/CD, scheduled tasks) without requiring browser-based authorization flows.

3. **Simplicity:** Personal Tokens are simpler to implement and maintain than OAuth. No redirect flow, no token refresh logic.

4. **Long-lived automation:** Personal Tokens can be configured without expiration dates (or with long expiration dates), suitable for automation that runs indefinitely.

5. **Consistent with existing architecture:** The current op-opsdevnz + 1Password integration already supports Personal Tokens.

**When to reconsider:**

- If we build a multi-user application that needs to act on behalf of different OpenCollective users
- If we need to integrate with OpenCollective's 2FA-protected operations (requires OAuth with special configuration)
- If OpenCollective introduces new authentication methods better suited to our use case

---

## Production Readiness Requirements

To move from development/testing to production, we need to address:

### 1. Token Rotation Strategy

**Problem:** Personal Tokens can expire. If a token expires, automation breaks.

**Requirements:**

- Document token expiration date (if set)
- Establish a rotation process (generate new token, update 1Password, test)
- Set up monitoring/alerting for token expiration (if possible)
- Document emergency rotation procedure (if token is compromised)

**Implementation:**

- Store token expiration date in 1Password item metadata or notes
- Create a runbook for token rotation
- Consider a scheduled task that checks token validity and alerts before expiration

### 2. Scope Minimization

**Problem:** Overly permissive tokens increase security risk if compromised.

**Requirements:**

- Review what scopes the token actually needs
- Grant minimal scopes required for the operations we perform
- Document which scopes are needed and why

**Implementation:**

- Audit oc-opsdevnz operations to determine required scopes
- Update token configuration in OpenCollective to grant only those scopes
- Document scope requirements in this design doc or in operational documentation

### 3. Service Account vs User Token

**Problem:** If the token is tied to a personal account (e.g., `john@opsdev.nz`) and that person leaves the collective, automation breaks.

**Requirements:**

- Consider creating a dedicated OpenCollective account for automation
- Use a service account (e.g., `automation@opsdev.nz`) instead of a personal account
- Document the account ownership and access model

**Implementation:**

- Create a dedicated OpenCollective account for OpsDev.nz automation
- Generate Personal Token from that account
- Store credentials in 1Password with clear ownership documentation
- Document who has access to the service account credentials

### 4. Documentation and Operational Procedures

**Problem:** Without documentation, token management becomes ad-hoc and error-prone.

**Requirements:**

- Document where the token lives in 1Password (vault, item name, field)
- Document what scopes the token has
- Document when the token expires (if applicable)
- Document how to rotate the token
- Document how to test the token (e.g., `oc-opsdevnz whoami`)

**Implementation:**

- Create operational documentation (runbook) for token management
- Include token metadata in 1Password item notes
- Link to this design doc from operational documentation

### 5. Environment Separation

**Problem:** Staging and production tokens should be separate to prevent accidental changes.

**Requirements:**

- Use separate tokens for staging and production
- Store tokens in separate 1Password items
- Ensure code/configuration clearly distinguishes between environments

**Implementation:**

- Staging token: `op://startmeup.nz/opencollective-staging/token`
- Production token: `op://startmeup.nz/opencollective-prod/token`
- Use `--staging` flag or `OC_SECRET_REF` environment variable to select environment

---

## Recommended Implementation

### 1. Create Service Account

Create a dedicated OpenCollective account for OpsDev.nz automation:

- Account name: `opsdevnz-automation` or similar
- Email: `automation@opsdev.nz` or similar
- Owned by: OpsDev.nz collective (not an individual)

### 2. Generate Personal Tokens

Generate two Personal Tokens (staging and production):

**Staging Token:**

- Account: `opsdevnz-automation` (or test account on staging)
- Scopes: `account`, `host` (minimum required for collective management)
- Expiration: None (or 1 year with rotation reminder)
- 1Password location: `op://startmeup.nz/opencollective-staging-automation/token`

**Production Token:**

- Account: `opsdevnz-automation`
- Scopes: `account`, `host` (minimum required)
- Expiration: 1 year (with rotation reminder 30 days before)
- 1Password location: `op://startmeup.nz/opencollective-prod-automation/token`

### 3. Update Configuration

Update environment variables and documentation:

```bash
# Staging
export OC_SECRET_REF="op://startmeup.nz/opencollective-staging-automation/token"

# Production
export OC_SECRET_REF="op://startmeup.nz/opencollective-prod-automation/token"
```

### 4. Create Operational Documentation

Create a runbook for token management:

- How to check token validity (`oc-opsdevnz whoami`)
- How to rotate tokens
- How to update 1Password
- Emergency procedures (token compromise)

### 5. Test and Validate

Test the new tokens:

- Verify staging token works with `oc-opsdevnz whoami --staging`
- Verify production token works with `oc-opsdevnz whoami`
- Verify CI/CD pipelines can resolve tokens from 1Password
- Verify local development can resolve tokens (via CLI or override)

---

## Open Questions

1. **What scopes do we actually need?** Audit oc-opsdevnz operations to determine minimum required scopes.

2. **Should we use a service account or a collective-owned account?** OpenCollective may not support "service accounts" in the traditional sense. We may need to create a user account owned by the collective.

3. **How do we monitor token expiration?** OpenCollective may not expose token expiration via API. We may need to track expiration dates manually in 1Password.

4. **What's the rotation process?** How do we rotate tokens without breaking automation? Do we need a grace period where both old and new tokens work?

---

## References

- [OpenCollective Personal Tokens Documentation](https://docs.opencollective.com/help/developers/personal-tokens.md)
- [OpenCollective OAuth Documentation](https://docs.opencollective.com/help/developers/oauth.md)
- [op-opsdevnz module](https://github.com/startmeup-nz/op-opsdevnz)
- [oc-opsdevnz module](https://github.com/startmeup-nz/oc-opsdevnz)
