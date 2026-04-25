import pytest
from starlette.testclient import TestClient

from adapters.mews.adapter import MewsAdapter
from adapters.mews.client import MewsClient
from tests.mews_mock.server import (
    SERVICE_ID,
    MewsMockState,
    build_mock_app,
)

_BASE = "http://mews-mock/api/connector/v1"


@pytest.fixture
def mock_state():
    state = MewsMockState()
    yield state
    state.reset()


@pytest.fixture
def mews_client(mock_state):
    app = build_mock_app(mock_state)
    http = TestClient(app, base_url="http://mews-mock")
    return MewsClient(
        client_token="test-token",
        access_token="test-access",
        _http_client=http,
        _base_url=_BASE,
    )


@pytest.fixture
def mews_adapter(mews_client):
    return MewsAdapter(client=mews_client, service_id=SERVICE_ID)
