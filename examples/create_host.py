"""
Minimal example: create/update an Organization (potential host) with currency and legal name.

Edit HOST below or pass a slug override via argv[1]. Uses staging by default and
token from OC_SECRET_REF/OC_TOKEN.
"""

import json
import sys
from typing import Dict, Any

from oc_opsdevnz import OpenCollectiveClient

HOST: Dict[str, Any] = {
    "name": "Example Host",
    "slug": "example-host",
    "legalName": "Example Host Ltd",
    "description": "Example host for Open Collective.",
    "website": "https://example.org",
    "currency": "USD",
    "tags": ["fiscal-host", "example"],
}

Q_ACCOUNT = """
query Account($slug: String!) {
  account(slug: $slug) {
    id
    slug
    name
    legalName
    type
    currency
    tags
    website
    socialLinks { type url }
  }
}
"""

MUTATION_CREATE = """
mutation CreateOrganization($input: OrganizationCreateInput!) {
  createOrganization(organization: $input) {
    id
    slug
    name
    type
  }
}
"""

MUTATION_EDIT = """
mutation EditAccount($account: AccountUpdateInput!) {
  editAccount(account: $account) {
    id
    slug
    name
    legalName
    currency
    tags
    website
    socialLinks { type url }
  }
}
"""


def upsert_website_link(links, website):
    if website is None:
        return links
    links = [link for link in links if (link or {}).get("type") != "WEBSITE"]
    links.append({"type": "WEBSITE", "url": website})
    return links


def main():
    host = dict(HOST)
    if len(sys.argv) > 1:
        host["slug"] = sys.argv[1]

    client = OpenCollectiveClient.for_staging()

    # Create if missing
    try:
        data = client.graphql(Q_ACCOUNT, {"slug": host["slug"]})
        account = data.get("account")
    except RuntimeError as e:
        account = None
        if "No account found with slug" not in str(e):
            raise

    if not account:
        print(f"[create] creating org {host['slug']}…")
        created = client.graphql(
            MUTATION_CREATE,
            {
                "input": {
                    "name": host["name"],
                    "slug": host["slug"],
                    "description": host.get("description", ""),
                    "website": host.get("website"),
                }
            },
        )["createOrganization"]
        account = created
        print("[created]", json.dumps(created, indent=2))
    else:
        print(f"[exists] {host['slug']} found; will update fields as needed")

    # Update fields (legalName/currency/tags/website)
    links = upsert_website_link(account.get("socialLinks") or [], host.get("website"))
    patch = {
        "id": account["id"],
        "name": host["name"],
        "description": host.get("description", ""),
        "legalName": host.get("legalName"),
        "currency": host.get("currency"),
        "tags": host.get("tags"),
        "socialLinks": links,
    }
    out = client.graphql(MUTATION_EDIT, {"account": patch})["editAccount"]
    print("[updated]", json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
