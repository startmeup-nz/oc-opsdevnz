# examples/seed_host_and_allocate.py
"""Seed a fiscal host and allocate earmarks to projects.

Demonstrates the two key ``addFunds`` patterns validated against the OC staging API:

1. **Self-referencing host seed** — credit the host with an opening balance
2. **Host→project allocation** — move funds from the host to a project

Prerequisites:
    - ``OC_SECRET_REF`` or ``OC_TOKEN`` environment variable set
    - Fiscal host account exists on the target OC environment
    - Project accounts exist if allocating

Usage::

    # Seed host on staging (default)
    OC_API_URL=https://api-staging.opencollective.com/graphql/v2 \\
      python examples/seed_host_and_allocate.py seed --amount 5606.04

    # Allocate to a project
    OC_API_URL=https://api-staging.opencollective.com/graphql/v2 \\
      python examples/seed_host_and_allocate.py allocate \\
        --project software-freedom-day-2026 \\
        --amount 655.50 \\
        --desc "SFD 2026 allocation: Cookies $250 | Facilitator $300 | Swag $105.50"

    # Verify balances
    OC_API_URL=https://api.opencollective.com/graphql/v2 \\
      python examples/seed_host_and_allocate.py balance startmeup-nz opsdevnz

The ``OC_API_URL`` environment variable determines the target. There is no
default — you must set it explicitly. This prevents accidental production writes.

Related:
    - docs/stories/financial-operations.md — full story and acceptance criteria
    - OpenCollective GraphQL API v2: https://docs.opencollective.com/help/developers/api
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from decimal import Decimal
from typing import Optional

from op_opsdevnz.onepassword import get_secret

from oc_opsdevnz.oc_client import OpenCollectiveClient

HOST_SLUG = "startmeup-nz"
CUT_IN_DATE = "2026-07-22T00:00:00Z"


# ---------------------------------------------------------------------------
# GraphQL operations
# ---------------------------------------------------------------------------

ADD_FUNDS = """
mutation AddFunds(
  $from: AccountReferenceInput!,
  $to: AccountReferenceInput!,
  $amount: AmountInput!,
  $description: String!,
  $hostFeePercent: Float!,
  $processedAt: DateTime
) {
  addFunds(
    fromAccount: $from,
    account: $to,
    amount: $amount,
    description: $description,
    hostFeePercent: $hostFeePercent,
    processedAt: $processedAt
  ) {
    id
    status
    amount { valueInCents currency }
  }
}
"""

BALANCE_QUERY = """
query Balance($slug: String!) {
  account(slug: $slug) {
    slug
    name
    stats {
      balance { valueInCents currency }
    }
  }
}
"""


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def _cents(amount: Decimal) -> int:
    """Convert dollars to cents using Decimal arithmetic (never float)."""
    return int(amount * 100)


def seed_host(client: OpenCollectiveClient, amount: Decimal, *, date: Optional[str] = None) -> dict:
    """Credit the host with an opening balance via self-referencing addFunds."""
    cents = _cents(amount)
    processed_at = date or CUT_IN_DATE

    print(f"Seeding {HOST_SLUG} with ${amount:,.2f} ({cents:,} cents)")
    print(f"  fromAccount: {HOST_SLUG} (self-referencing)")
    print(f"  processedAt: {processed_at}")
    print()

    result = client.graphql(ADD_FUNDS, {
        "from": {"slug": HOST_SLUG},
        "to": {"slug": HOST_SLUG},
        "amount": {"valueInCents": cents, "currency": "NZD"},
        "description": f"Host opening balance — equity seed at cut-in {processed_at[:10]}",
        "hostFeePercent": 0,
        "processedAt": processed_at,
    })

    tx = result["addFunds"]
    print(f"  ID:     {tx['id']}")
    print(f"  Status: {tx['status']}")
    print(f"  Amount: {tx['amount']['valueInCents'] / 100:,.2f} {tx['amount']['currency']}")
    print("  \u2713 Host seeded.\n")
    return tx


def allocate_to_project(
    client: OpenCollectiveClient,
    project_slug: str,
    amount: Decimal,
    description: str,
    *,
    date: Optional[str] = None,
) -> dict:
    """Allocate funds from the host to a project."""
    cents = _cents(amount)
    processed_at = date or CUT_IN_DATE

    print(f"Allocating ${amount:,.2f} from {HOST_SLUG} \u2192 {project_slug}")
    print(f"  {description}")
    print()

    result = client.graphql(ADD_FUNDS, {
        "from": {"slug": HOST_SLUG},
        "to": {"slug": project_slug},
        "amount": {"valueInCents": cents, "currency": "NZD"},
        "description": description,
        "hostFeePercent": 0,
        "processedAt": processed_at,
    })

    tx = result["addFunds"]
    print(f"  ID:     {tx['id']}")
    print(f"  Status: {tx['status']}")
    print(f"  Amount: {tx['amount']['valueInCents'] / 100:,.2f} {tx['amount']['currency']}")
    print("  \u2713 Funds allocated.\n")
    return tx


def show_balances(client: OpenCollectiveClient, slugs: list[str]) -> None:
    """Print balances for one or more account slugs."""
    print("── Balances ──")
    for slug in slugs:
        result = client.graphql(BALANCE_QUERY, {"slug": slug})
        acc = result.get("account")
        if acc is None:
            print(f"  {slug}: not found")
            continue
        bal = acc["stats"]["balance"]
        print(f"  {acc['slug']:40s}  ${bal['valueInCents'] / 100:>10,.2f} {bal['currency']}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_client() -> OpenCollectiveClient:
    """Resolve the token and build a client. Requires OC_API_URL in env."""
    api_url = os.getenv("OC_API_URL")
    if not api_url:
        print("error: OC_API_URL environment variable must be set", file=sys.stderr)
        print("  staging: export OC_API_URL=https://api-staging.opencollective.com/graphql/v2", file=sys.stderr)
        print("  production: export OC_API_URL=https://api.opencollective.com/graphql/v2", file=sys.stderr)
        sys.exit(64)

    token = get_secret(secret_ref_env="OC_SECRET_REF")
    return OpenCollectiveClient(api_url=api_url, token=token, allow_prod=True)


def _amount_type(value: str) -> Decimal:
    """Argparse type for dollar amounts — ensures Decimal, never float."""
    return Decimal(value)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed host balance and allocate funds to projects via addFunds.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # seed
    p_seed = sub.add_parser("seed", help="Seed the host with an opening balance")
    p_seed.add_argument("--amount", type=_amount_type, default=Decimal("5606.04"),
                        help="Amount in NZD (default: 5606.04)")
    p_seed.add_argument("--date", default=None,
                        help=f"processedAt datetime (default: {CUT_IN_DATE})")

    # allocate
    p_alloc = sub.add_parser("allocate", help="Allocate funds from host to a project")
    p_alloc.add_argument("--project", required=True, help="Project slug")
    p_alloc.add_argument("--amount", type=_amount_type, required=True, help="Amount in NZD")
    p_alloc.add_argument("--desc", required=True, help="Description / line-item breakdown")
    p_alloc.add_argument("--date", default=None,
                         help=f"processedAt datetime (default: {CUT_IN_DATE})")

    # balance
    p_bal = sub.add_parser("balance", help="Show account balances")
    p_bal.add_argument("slugs", nargs="+", help="One or more account slugs")

    args = parser.parse_args()
    client = _build_client()

    if args.command == "seed":
        seed_host(client, args.amount, date=args.date)
        show_balances(client, [HOST_SLUG])

    elif args.command == "allocate":
        allocate_to_project(client, args.project, args.amount, args.desc, date=args.date)
        show_balances(client, [HOST_SLUG, args.project])

    elif args.command == "balance":
        show_balances(client, args.slugs)


if __name__ == "__main__":
    main()
