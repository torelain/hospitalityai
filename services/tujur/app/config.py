"""Centralised env-var validation. Fails fast with a clear list of missing keys."""

import os
from dataclasses import dataclass

# Minimal set required for the app to boot. Graph-related vars are optional for now —
# the webhook handler will fail at request time if they're not set, but /health and
# DB-only paths work without them. Restore the full list once the pilot mailbox is wired.
REQUIRED_ALWAYS = ["ANTHROPIC_API_KEY", "DATABASE_URL"]
# REQUIRED_FOR_GRAPH = [
#     "AZURE_CLIENT_ID",
#     "AZURE_CLIENT_SECRET",
#     "HOTEL_TENANT_ID",
#     "HOTEL_MAILBOX",
#     "GRAPH_WEBHOOK_URL",
#     "GRAPH_WEBHOOK_CLIENT_STATE",
# ]


@dataclass
class Config:
    anthropic_api_key: str
    database_url: str
    azure_client_id: str = ""
    azure_client_secret: str = ""
    hotel_tenant_id: str = ""
    hotel_mailbox: str = ""
    graph_webhook_url: str = ""
    graph_webhook_client_state: str = ""


def load() -> Config:
    missing = [v for v in REQUIRED_ALWAYS if not os.environ.get(v)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
            + ". See .env.example for the full list."
        )
    return Config(
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
        database_url=os.environ["DATABASE_URL"],
        azure_client_id=os.environ.get("AZURE_CLIENT_ID", ""),
        azure_client_secret=os.environ.get("AZURE_CLIENT_SECRET", ""),
        hotel_tenant_id=os.environ.get("HOTEL_TENANT_ID", ""),
        hotel_mailbox=os.environ.get("HOTEL_MAILBOX", ""),
        graph_webhook_url=os.environ.get("GRAPH_WEBHOOK_URL", ""),
        graph_webhook_client_state=os.environ.get("GRAPH_WEBHOOK_CLIENT_STATE", ""),
    )
