from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from domain.models import InboundEmail
from .auth import GraphTokenCache

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
SUBSCRIPTION_LIFETIME_MINUTES = 4230  # Graph max for mail resources (~70.5 hours)


class GraphInboundClient:
    def __init__(
        self,
        token_cache: GraphTokenCache,
        _http_client: httpx.Client | None = None,
    ):
        self._tokens = token_cache
        self._http = _http_client or httpx.Client(timeout=10.0)

    def fetch_message(self, mailbox: str, message_id: str) -> InboundEmail:
        response = self._http.get(
            f"{GRAPH_BASE}/users/{mailbox}/messages/{message_id}",
            headers=self._auth_headers(),
            params={
                "$select": "id,internetMessageId,from,toRecipients,subject,body,receivedDateTime",
            },
        )
        response.raise_for_status()
        return _parse_message(response.json())

    def create_subscription(self, mailbox: str, webhook_url: str, client_state: str) -> dict[str, Any]:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=SUBSCRIPTION_LIFETIME_MINUTES)
        response = self._http.post(
            f"{GRAPH_BASE}/subscriptions",
            headers=self._auth_headers(),
            json={
                "changeType": "created",
                "notificationUrl": webhook_url,
                "resource": f"users/{mailbox}/mailFolders('inbox')/messages",
                "expirationDateTime": _isoformat(expires_at),
                "clientState": client_state,
            },
        )
        response.raise_for_status()
        return response.json()

    def renew_subscription(self, subscription_id: str) -> dict[str, Any]:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=SUBSCRIPTION_LIFETIME_MINUTES)
        response = self._http.patch(
            f"{GRAPH_BASE}/subscriptions/{subscription_id}",
            headers=self._auth_headers(),
            json={"expirationDateTime": _isoformat(expires_at)},
        )
        response.raise_for_status()
        return response.json()

    def delete_subscription(self, subscription_id: str) -> None:
        response = self._http.delete(
            f"{GRAPH_BASE}/subscriptions/{subscription_id}",
            headers=self._auth_headers(),
        )
        if response.status_code not in (200, 204, 404):
            response.raise_for_status()

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._tokens.get()}"}


def parse_notification(payload: dict) -> list[dict]:
    """Returns the list of change-notifications from a Graph webhook POST body."""
    return payload.get("value", [])


def _parse_message(message: dict) -> InboundEmail:
    sender = message.get("from", {}).get("emailAddress", {}) or {}
    to_recipients = message.get("toRecipients") or []
    to_email = (to_recipients[0]["emailAddress"]["address"] if to_recipients else "") or ""
    body = message.get("body", {}) or {}
    body_text = body.get("content", "") if body.get("contentType", "").lower() == "text" else _strip_html(
        body.get("content", "")
    )
    received_raw = message.get("receivedDateTime")
    received_at = (
        datetime.fromisoformat(received_raw.replace("Z", "+00:00"))
        if received_raw
        else datetime.now(timezone.utc)
    )

    return InboundEmail(
        message_id=message.get("internetMessageId") or message["id"],
        from_email=sender.get("address", ""),
        from_name=sender.get("name", ""),
        to_email=to_email,
        subject=message.get("subject", "") or "",
        text_body=body_text,
        received_at=received_at,
    )


def _strip_html(html: str) -> str:
    """Cheap HTML→text fallback. Good enough for PoC; swap for BeautifulSoup if needed."""
    import re

    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def _isoformat(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")
