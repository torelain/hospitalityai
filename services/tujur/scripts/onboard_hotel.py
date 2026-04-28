"""One-time onboarding: creates the Graph subscription on the hotel inbox and stores it.

Run after the hotel admin has granted consent and provided HOTEL_TENANT_ID + HOTEL_MAILBOX.

Usage (from services/tujur/):
    python -m scripts.onboard_hotel

Expects: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, HOTEL_TENANT_ID, HOTEL_MAILBOX,
         GRAPH_WEBHOOK_URL, GRAPH_WEBHOOK_CLIENT_STATE, DATABASE_URL
"""

import os
import sys
from datetime import datetime

from dotenv import load_dotenv

from adapters.db.connection import make_pool
from adapters.db.migrations import run as run_migrations
from adapters.graph.auth import GraphTokenCache
from adapters.graph.inbound import GraphInboundClient

load_dotenv()


def main() -> int:
    required = [
        "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET",
        "HOTEL_TENANT_ID", "HOTEL_MAILBOX",
        "GRAPH_WEBHOOK_URL", "GRAPH_WEBHOOK_CLIENT_STATE",
        "DATABASE_URL",
    ]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        return 1

    pool = make_pool(os.environ["DATABASE_URL"])
    run_migrations(pool)

    mailbox = os.environ["HOTEL_MAILBOX"]
    webhook_url = os.environ["GRAPH_WEBHOOK_URL"]
    client_state = os.environ["GRAPH_WEBHOOK_CLIENT_STATE"]

    token_cache = GraphTokenCache(
        tenant_id=os.environ["HOTEL_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )
    graph = GraphInboundClient(token_cache=token_cache)

    print(f"Creating subscription for {mailbox} → {webhook_url}")
    subscription = graph.create_subscription(mailbox, webhook_url, client_state)
    expires_at = datetime.fromisoformat(subscription["expirationDateTime"].replace("Z", "+00:00"))
    print(f"  ✓ subscription_id={subscription['id']} expires_at={expires_at.isoformat()}")

    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO graph_subscriptions (subscription_id, hotel_mailbox, client_state, expires_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (hotel_mailbox) DO UPDATE
                SET subscription_id = EXCLUDED.subscription_id,
                    client_state    = EXCLUDED.client_state,
                    expires_at      = EXCLUDED.expires_at
            """,
            (subscription["id"], mailbox, client_state, expires_at),
        )

    pool.close()
    print("  ✓ persisted in graph_subscriptions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
