"""Smoke test: verifies AZURE_* + HOTEL_* env vars work against Microsoft Graph.

Usage (from services/tujur/):
    python -m scripts.smoke_test_graph

Expects: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, HOTEL_TENANT_ID, HOTEL_MAILBOX
"""

import os
import sys

import httpx
from dotenv import load_dotenv

from adapters.graph.auth import GraphTokenCache

load_dotenv()


def main() -> int:
    required = ["AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "HOTEL_TENANT_ID", "HOTEL_MAILBOX"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        return 1

    cache = GraphTokenCache(
        tenant_id=os.environ["HOTEL_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )

    print("Acquiring access token…")
    token = cache.get()
    print(f"  ✓ token (length {len(token)})")

    mailbox = os.environ["HOTEL_MAILBOX"]
    print(f"Probing GET /users/{mailbox}/messages?$top=1 …")
    response = httpx.get(
        f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages",
        headers={"Authorization": f"Bearer {token}"},
        params={"$top": 1, "$select": "id,subject,receivedDateTime"},
        timeout=10.0,
    )
    print(f"  → HTTP {response.status_code}")

    if response.is_success:
        messages = response.json().get("value", [])
        if messages:
            m = messages[0]
            print(f"  ✓ inbox accessible — newest message: {m.get('subject', '(no subject)')}")
        else:
            print("  ✓ inbox accessible — currently empty")
        return 0

    print(f"  ✗ {response.text}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
