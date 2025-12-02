# Changelog

## 0.1.1 (unreleased)
- Add project YAML/CLI support (`oc-opsdevnz projects`) to create/update projects under a parent collective.
- Fix project creation payload: parent is passed as a separate variable to `createProject` (not inside `ProjectCreateInput`).
- Refresh README/examples.

## 0.1.0
- Switch to an httpx GraphQL client with staging-first guardrails and redacted errors.
- Add CLI helpers for whoami, host upserts, and collective create/apply flows from YAML/JSON.
- Provide host/collective helper functions for reuse and tests with mocked HTTP responses.
- Add governance docs (CONTRIBUTING, SECURITY, CODEOWNERS, Code of Conduct).
