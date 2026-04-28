import threading
import time

import httpx


class GraphTokenCache:
    """Lazy in-memory cache for Microsoft Graph access tokens (client_credentials flow).

    Tokens are valid for ~60 minutes. We refresh proactively when less than 5 minutes
    are left, so callers never see an expired token.
    """

    REFRESH_BUFFER_SECONDS = 300

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        _http_client: httpx.Client | None = None,
    ):
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._http = _http_client or httpx.Client(timeout=10.0)
        self._token: str | None = None
        self._expires_at: float = 0.0
        self._lock = threading.Lock()

    def get(self) -> str:
        with self._lock:
            if not self._token or time.time() > self._expires_at - self.REFRESH_BUFFER_SECONDS:
                self._refresh()
            return self._token  # type: ignore[return-value]

    def _refresh(self) -> None:
        response = self._http.post(
            f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/v2.0/token",
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials",
            },
        )
        response.raise_for_status()
        body = response.json()
        self._token = body["access_token"]
        self._expires_at = time.time() + body["expires_in"]
