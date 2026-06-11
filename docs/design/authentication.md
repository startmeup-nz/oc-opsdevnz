# Authentication Design for oc-opsdevnz

**Status:** Draft<br />
**Created:** 2026-06-11<br />
**Last Reviewed:** 2026-06-12<br />
**Author:** opsdev

---

## Problem Statement

oc-opsdevnz needs to authenticate with the OpenCollective API to manage collectives, hosts, and projects. The authentication strategy must:

1. Work for automation (CI/CD, scheduled tasks)
2. Work for local development
3. Be secure and maintainable
4. Support both staging and production environments

---

## Current Architecture

### Secret Resolution (op-opsdevnz)

The `op-opsdevnz` module resolves secrets from 1Password. It accepts `op://` references (e.g. `op://vault/item/field`) and supports two resolution methods:

- **SDK:** Uses `OP_SERVICE_ACCOUNT_TOKEN` environment variable
- **CLI:** Falls back to the `op` binary if installed and authenticated

It returns the secret value plus metadata about which resolver was used.

### OpenCollective Client (oc-opsdevnz)

The `oc-opsdevnz` module uses `op-opsdevnz` to obtain the OpenCollective API token:

- `OC_SECRET_REF` environment variable points to the 1Password reference
- `OC_TOKEN` environment variable can override for local testing
- The `Personal-Token` HTTP header is used for API authentication

---

## OpenCollective Authentication Options

### 1. Personal Tokens

User-scoped API tokens tied to an OpenCollective account.

- Scoped access (email, account, expenses, orders, transactions, etc.)
- Configurable expiration
- Simple to use: pass token in `Personal-Token` HTTP header
- No user interaction required — suitable for headless automation

**Limitations:** Tied to a user account; no built-in refresh; rotation is manual.

### 2. OAuth 2.0 (Authorization Code Flow)

Standard OAuth 2.0 flow for multi-user applications.

- Requires browser-based user interaction (redirect flow)
- Access tokens expire and require refresh
- Can act on behalf of multiple users

**Limitations:** Not suitable for headless automation; more complex to implement; requires registering an OAuth application.

### 3. OpenID Connect (OIDC)

Not currently supported by OpenCollective. OIDC support has been raised as a [feature request](https://github.com/opencollective/opencollective/issues/7918) but has not been implemented. OpenCollective's API access is limited to Personal Tokens or OAuth 2.0.

---

## Decision: Personal Tokens

**Rationale:**

1. **Automation-first:** We are automating tasks for our own collective, not building a multi-user application.
2. **Headless-compatible:** Personal Tokens work in CI/CD and scheduled tasks without a browser flow.
3. **Simplicity:** No redirect flow, no token refresh logic.
4. **Consistent with existing architecture:** The `op-opsdevnz` + 1Password integration already supports this pattern.

**When to reconsider:**

- We build a multi-user application that needs to act on behalf of different OpenCollective users
- We need to integrate with 2FA-protected operations (requires OAuth with special configuration)
- OpenCollective introduces a better-suited authentication method

---

## Production Readiness Requirements

### 1. Service Account

Tokens must not be tied to an individual's account. If that person leaves the collective, automation breaks.

**Requirements:**

- Create a dedicated OpenCollective account for OpsDev.nz automation (e.g. `opsdevnz-automation`)
- Use a shared email address (e.g. `automation@opsdev.nz`) — **this address must be created and monitored before the service account is registered**, as OpenCollective sends account recovery and security alerts to it
- Document ownership and access in 1Password item notes

### 2. Scope Minimisation

**Status: Open — see [Open Questions](#open-questions)**

Overly permissive tokens increase risk if compromised. Required scopes must be audited before tokens are generated for production. The implementation section uses `account` and `host` as a placeholder pending that audit.

### 3. Token Rotation

Personal Tokens have no built-in refresh mechanism. Rotation must be handled manually.

**Rotation procedure:**

1. Generate a new token in OpenCollective under the service account
2. Update the relevant 1Password item
3. Verify with `oc-opsdevnz whoami [--staging]`
4. Revoke the old token

Because `op-opsdevnz` resolves secrets at runtime, the switchover is atomic — no grace period with dual valid tokens is needed.

**Expiry policy:**

- Staging: no expiration (lower risk, simplifies development)
- Production: 1 year, with a manual reminder set 30 days before expiry

Store the expiration date in the 1Password item notes field. OpenCollective does not currently expose token expiration via API, so this must be tracked manually.

### 4. Environment Separation

Staging and production tokens must be separate to prevent accidental cross-environment changes.

| Environment | 1Password reference |
|-------------|---------------------|
| Staging | `op://startmeup.nz/opencollective-staging-automation/token` |
| Production | `op://startmeup.nz/opencollective-prod-automation/token` |

Select environment via `--staging` flag or `OC_SECRET_REF` environment variable.

### 5. Operational Documentation

A runbook must be created covering:

- How to check token validity (`oc-opsdevnz whoami`)
- Token rotation procedure (see above)
- Emergency procedure for token compromise (revoke immediately, rotate, audit API logs)
- Where tokens live in 1Password and what scopes they hold

---

## Implementation Plan

### Step 1: Create the service account

Create a dedicated OpenCollective account:

- **Account name:** `opsdevnz-automation` (or similar)
- **Email:** `automation@opsdev.nz` — must be a real, monitored mailbox or forwarding alias before this step
- **Ownership:** Document in 1Password who controls the credentials

### Step 2: Generate tokens

**Staging token:**

- Account: `opsdevnz-automation` (staging environment)
- Scopes: TBD (see Open Questions)
- Expiration: None
- 1Password: `op://startmeup.nz/opencollective-staging-automation/token`

**Production token:**

- Account: `opsdevnz-automation`
- Scopes: TBD (see Open Questions)
- Expiration: 1 year (note expiry date in 1Password item)
- 1Password: `op://startmeup.nz/opencollective-prod-automation/token`

### Step 3: Update configuration

```bash
# Staging
export OC_SECRET_REF="op://startmeup.nz/opencollective-staging-automation/token"

# Production
export OC_SECRET_REF="op://startmeup.nz/opencollective-prod-automation/token"
```

### Step 4: Validate

- `oc-opsdevnz whoami --staging` confirms staging token resolves and authenticates
- `oc-opsdevnz whoami` confirms production token resolves and authenticates
- CI/CD pipelines can resolve tokens via `OP_SERVICE_ACCOUNT_TOKEN`
- Local development can resolve tokens via the `op` CLI

### Step 5: Write the runbook

Deliver operational documentation covering token management, rotation, and emergency procedures. Link from this document once complete.

---

## Open Questions

1. **What scopes are actually required?** Audit `oc-opsdevnz` operations to determine the minimum required set. Tokens should not be generated for production until this is resolved.

2. **Does OpenCollective support collective-owned accounts?** OpenCollective may not have a formal "service account" concept. We may need a regular user account with a shared email. Confirm before Step 1.

3. **How do we monitor token expiration?** OpenCollective does not appear to expose expiration via API. Confirm this, and if true, establish a calendar reminder or scheduled task as a compensating control.

---

## References

- [OpenCollective Personal Tokens Documentation](https://documentation.opencollective.com/development/personal-tokens)
- [OpenCollective OAuth Documentation](https://documentation.opencollective.com/development/oauth)
- [OpenCollective OIDC Feature Request #7918](https://github.com/opencollective/opencollective/issues/7918)
- [op-opsdevnz module](https://github.com/startmeup-nz/op-opsdevnz)
- [oc-opsdevnz module](https://github.com/startmeup-nz/oc-opsdevnz)
