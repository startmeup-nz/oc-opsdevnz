# examples/list_expenses.py
import json
import os
import sys

from op_opsdevnz.onepassword import get_secret

from oc_opsdevnz.oc_client import PROD_URL, OpenCollectiveClient


def main():
    if len(sys.argv) < 2:
        print("Usage: python examples/list_expenses.py <account-slug> [STATUS...]", file=sys.stderr)
        print("STATUS options: PENDING APPROVED PAID REJECTED CANCELED DRAFT", file=sys.stderr)
        sys.exit(64)

    slug, *statuses = sys.argv[1:]
    statuses = [s.upper() for s in (statuses or ["PENDING", "APPROVED", "PAID"])]

    token = get_secret(secret_ref_env="OC_SECRET_REF")
    api_url = os.getenv("OC_API_URL")
    oc = OpenCollectiveClient(api_url=api_url, token=token, allow_prod=api_url == PROD_URL)

    # NOTE: the OC GraphQL `expenses` query no longer accepts a plain
    # `[ExpenseStatus!]` list for `status` (it now expects `ExpenseStatusFilter`),
    # and `amount` is a plain Int (cents) rather than an object. We fetch a
    # larger page and filter client-side to stay schema-compatible.
    q = """
    query ListExpenses($slug: String!) {
      expenses(account: { slug: $slug }, limit: 100) {
        nodes {
          id
          legacyId
          status
          type
          description
          amount
          currency
          payee { slug name }
          createdAt
        }
      }
    }
    """
    res = oc.execute(q, {"slug": slug})
    nodes = (res.get("expenses") or {}).get("nodes") or []
    if statuses:
        nodes = [n for n in nodes if (n.get("status") or "").upper() in statuses]
    print(json.dumps({"expenses": {"nodes": nodes}}, indent=2))

if __name__ == "__main__":
    main()
