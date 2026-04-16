import httpx


class MewsClient:
    BASE_URL_DEMO = "https://api.mews-demo.com/api/connector/v1"
    BASE_URL_PROD = "https://api.mews.com/api/connector/v1"

    def __init__(self, client_token: str, access_token: str, demo: bool = True):
        self._credentials = {
            "ClientToken": client_token,
            "AccessToken": access_token,
            "Client": "hospitalityai/email-processor",
        }
        self._base_url = self.BASE_URL_DEMO if demo else self.BASE_URL_PROD

    def post(self, endpoint: str, payload: dict) -> dict:
        response = httpx.post(
            f"{self._base_url}/{endpoint}",
            json={**self._credentials, **payload},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()
