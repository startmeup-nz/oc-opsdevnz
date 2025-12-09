# Changelog

## 0.2.0 (unreleased)
- Default API target is production; require `--staging`/`--test` to hit staging. `--prod` remains accepted for explicitness.
- Update docs/examples to reflect prod-first default and staging flags.
- Bump version command/config alias tests to cover new flags.

## 0.1.2
- Add `--config` alias to all CLI commands so callers can pass any config filename without changing defaults.
- Refresh docs/examples to clarify staging-first usage and flexible config naming.
- Add `version` subcommand to print the installed package version.
- Hosts: apply `long_description`/`longDescription` from YAML directly (no helper script needed).

## 0.1.1
- Add project YAML/CLI support (`oc-opsdevnz projects`) to create/update projects under a parent collective.
- Fix project creation payload: parent is passed as a separate variable to `createProject` (not inside `ProjectCreateInput`).
- Refresh README/examples.

## 0.1.0
- Switch to an httpx GraphQL client with staging-first guardrails and redacted errors.
- Add CLI helpers for whoami, host upserts, and collective create/apply flows from YAML/JSON.
- Provide host/collective helper functions for reuse and tests with mocked HTTP responses.
- Add governance docs (CONTRIBUTING, SECURITY, CODEOWNERS, Code of Conduct).
