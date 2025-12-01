# examples/create_and_pay_expense.py
import json
import os
import sys

from op_opsdevnz.onepassword import get_secret
from oc_opsdevnz.oc_client import OpenCollectiveClient, PROD_URL

CREATE = """
mutation CreateExpense($input: ExpenseCreateInput!) {
  createExpense(expense: $input) {
    expense { id legacyId status amount { valueInCents currency } }
  }
}
"""

PROCESS = """
mutation Process($id: String!, $action: ExpenseProcessAction!) {
  processExpense(expense: { id: $id }, action: $action) {
    expense { id status }
  }
}
"""

def main():
    if len(sys.argv) < 3:
        print("Usage: python examples/create_and_pay_expense.py <account-slug> <payee-slug>", file=sys.stderr)
        sys.exit(64)

    account_slug = sys.argv[1]
    payee_slug = sys.argv[2]

    token = get_secret(secret_ref_env="OC_SECRET_REF")
    api_url = os.getenv("OC_API_URL")
    oc = OpenCollectiveClient(api_url=api_url, token=token, allow_prod=api_url == PROD_URL)

    # 1) Create
    create_vars = {
        "input": {
            "type": "REIMBURSEMENT",
            "account": { "slug": account_slug },
            "payee":   { "slug": payee_slug },
            "currency": "USD",
            "description": "Staging test expense",
            "items": [
                { "amount": { "valueInCents": 1234 }, "description": "Receipt #1" }
            ],
            "payoutMethod": { "type": "ACCOUNT_BALANCE" }
        }
    }
    created = oc.execute(CREATE, create_vars)
    expense_id = created["createExpense"]["expense"]["id"]
    print("Created:", json.dumps(created, indent=2))

    # 2) Approve
    approved = oc.execute(PROCESS, {"id": expense_id, "action": "APPROVE"})
    print("Approved:", json.dumps(approved, indent=2))

    # 3) Pay (use PAY to simulate; adjust action if you want a specific flow)
    paid = oc.execute(PROCESS, {"id": expense_id, "action": "PAY"})
    print("Paid:", json.dumps(paid, indent=2))

if __name__ == "__main__":
    main()
