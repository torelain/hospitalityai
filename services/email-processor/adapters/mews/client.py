import httpx


class MewsClient:
    BASE_URL_DEMO = "https://api.mews-demo.com/api/connector/v1"
    BASE_URL_PROD = "https://api.mews.com/api/connector/v1"

    def __init__(
        self,
        client_token: str,
        access_token: str,
        demo: bool = True,
        _http_client: httpx.Client | None = None,
        _base_url: str | None = None,
    ):
        self._credentials = {
            "ClientToken": client_token,
            "AccessToken": access_token,
            "Client": "hospitalityai/email-processor",
        }
        self._base_url = _base_url or (self.BASE_URL_DEMO if demo else self.BASE_URL_PROD)
        self._http = _http_client or httpx.Client(timeout=10.0)

    def post(self, endpoint: str, payload: dict) -> dict:
        response = self._http.post(
            f"{self._base_url}/{endpoint}",
            json={**self._credentials, **payload},
        )
        response.raise_for_status()
        return response.json()
