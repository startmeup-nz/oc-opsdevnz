# examples/list_expenses.py
import json
import os
import sys

from op_opsdevnz.onepassword import get_secret
from oc_opsdevnz.oc_client import OpenCollectiveClient, PROD_URL

def main():
    if len(sys.argv) < 2:
        print("Usage: python examples/list_expenses.py <account-slug> [STATUS...]", file=sys.stderr)
        print("STATUS options: PENDING APPROVED PAID REJECTED CANCELED DRAFT", file=sys.stderr)
        sys.exit(64)

    slug, *statuses = sys.argv[1:]
    statuses = statuses or ["PENDING", "APPROVED", "PAID"]

    token = get_secret(secret_ref_env="OC_SECRET_REF")
    api_url = os.getenv("OC_API_URL")
    oc = OpenCollectiveClient(api_url=api_url, token=token, allow_prod=api_url == PROD_URL)

    q = """
    query ListExpenses($slug: String!, $status: [ExpenseStatus!]) {
      expenses(account: { slug: $slug }, limit: 20, status: $status) {
        nodes {
          id legacyId status type description
          amount { valueInCents currency }
          payee { slug name }
          createdAt
        }
      }
    }
    """
    res = oc.execute(q, {"slug": slug, "status": statuses})
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
