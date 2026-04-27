"""Centralised env-var validation. Fails fast with a clear list of missing keys."""

import os
from dataclasses import dataclass

REQUIRED_ALWAYS = ["ANTHROPIC_API_KEY", "DATABASE_URL"]
REQUIRED_FOR_GRAPH = [
    "AZURE_CLIENT_ID",
    "AZURE_CLIENT_SECRET",
    "HOTEL_TENANT_ID",
    "HOTEL_MAILBOX",
    "GRAPH_WEBHOOK_URL",
    "GRAPH_WEBHOOK_CLIENT_STATE",
]


@dataclass
class Config:
    anthropic_api_key: str
    database_url: str
    azure_client_id: str
    azure_client_secret: str
    hotel_tenant_id: str
    hotel_mailbox: str
    graph_webhook_url: str
    graph_webhook_client_state: str


def load() -> Config:
    missing = [v for v in REQUIRED_ALWAYS + REQUIRED_FOR_GRAPH if not os.environ.get(v)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
            + ". See .env.example for the full list."
        )
    return Config(
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
        database_url=os.environ["DATABASE_URL"],
        azure_client_id=os.environ["AZURE_CLIENT_ID"],
        azure_client_secret=os.environ["AZURE_CLIENT_SECRET"],
        hotel_tenant_id=os.environ["HOTEL_TENANT_ID"],
        hotel_mailbox=os.environ["HOTEL_MAILBOX"],
        graph_webhook_url=os.environ["GRAPH_WEBHOOK_URL"],
        graph_webhook_client_state=os.environ["GRAPH_WEBHOOK_CLIENT_STATE"],
    )
