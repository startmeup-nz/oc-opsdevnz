# oc_opsdevnz
OpenCollective client for OpsDev.NZ (staging-first). Resolves tokens from 1Password via `op-opsdevnz`, with optional `OC_TOKEN` override. Defaults to the staging API unless you explicitly select prod.

## Install
```bash
pip install oc-opsdevnz op-opsdevnz
```

## Quick start (staging)
```bash
export OC_SECRET_REF="op://startmeup.nz/api-staging.opencollective.com/credential"  # or set OC_TOKEN
python -m oc_opsdevnz.examples.whoami
```
This uses the staging API by default. Override with `OC_API_URL` if needed, or:
```python
from oc_opsdevnz import OpenCollectiveClient
client = OpenCollectiveClient.for_staging()
# or explicitly prod (only if you mean it):
prod_client = OpenCollectiveClient.for_prod()
```

## CLI example (whoami)
See `examples/whoami.py` for a minimal GraphQL query; adjust the slug to your collective/host.

## Other examples
- `examples/create_host.py` — create/update an organization (host) with currency/legal name/website/tags.
- `examples/get_admins.py` — list admins for a slug.
- `examples/create_and_pay_expense.py`, `examples/list_expenses.py`, `examples/get_balance.py` — expense/balance flows.

## Notes
- Tokens come from 1Password (`OC_SECRET_REF`) via `op-opsdevnz`; `OC_TOKEN` is an optional override.
- Prod is opt-in: use `OpenCollectiveClient.for_prod()` or set `OC_API_URL` to the prod GraphQL endpoint.
- Debugging auth: set `OC_DEBUG=1` to include a redacted response snippet and token fingerprint (SHA256 prefix) in errors. Body is omitted by default to avoid leaking tokens.
