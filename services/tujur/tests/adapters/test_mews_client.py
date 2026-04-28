import json

import httpx
import pytest
import respx

from adapters.mews.client import MewsClient


@pytest.fixture
def client():
    return MewsClient(
        client_token="test-client-token",
        access_token="test-access-token",
        demo=True,
    )


@respx.mock
def test_post_merges_credentials_with_payload(client):
    route = respx.post(
        "https://api.mews-demo.com/api/connector/v1/configuration/get"
    ).mock(return_value=httpx.Response(200, json={"NowUtc": "2026-04-16T00:00:00Z"}))

    client.post("configuration/get", {})

    assert route.called
    sent = json.loads(route.calls[0].request.content)
    assert sent["ClientToken"] == "test-client-token"
    assert sent["AccessToken"] == "test-access-token"
    assert sent["Client"] == "hospitalityai/tujur"


@respx.mock
def test_post_raises_on_non_200(client):
    respx.post(
        "https://api.mews-demo.com/api/connector/v1/configuration/get"
    ).mock(return_value=httpx.Response(429, json={"Message": "Too many requests"}))

    with pytest.raises(httpx.HTTPStatusError):
        client.post("configuration/get", {})
