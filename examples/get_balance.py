# examples/get_balance.py
from op_opsdevnz.onepassword import get_secret
from oc_opsdevnz.oc_client import OpenCollectiveClient
import os, sys, json

def main():
    if len(sys.argv) != 2:
        print("Usage: python examples/get_balance.py <account-slug>", file=sys.stderr)
        sys.exit(64)

    slug = sys.argv[1]
    token = get_secret(secret_ref_env="OC_SECRET_REF")
    oc = OpenCollectiveClient(token, base_url=os.getenv("OC_API_URL"))

    q = """
    query GetAccount($slug: String!) {
      account(slug: $slug) {
        id slug name type isHost
        host { id slug name }
        stats { balance { valueInCents currency } }
      }
    }
    """
    res = oc.execute(q, {"slug": slug})
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
