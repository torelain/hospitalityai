import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.security import require_cron_token


def _make_app(cron_token: str) -> FastAPI:
    app = FastAPI()
    app.state.cron_token = cron_token

    from fastapi import Depends

    @app.post("/protected", dependencies=[Depends(require_cron_token)])
    def protected():
        return {"ok": True}

    return app


def test_returns_503_when_token_not_configured():
    client = TestClient(_make_app(cron_token=""))
    response = client.post("/protected")
    assert response.status_code == 503


def test_returns_401_when_token_missing():
    client = TestClient(_make_app(cron_token="secret-xyz"))
    response = client.post("/protected")
    assert response.status_code == 401


def test_returns_401_when_token_mismatch():
    client = TestClient(_make_app(cron_token="secret-xyz"))
    response = client.post("/protected", headers={"X-Cron-Token": "wrong"})
    assert response.status_code == 401


def test_passes_when_token_matches():
    client = TestClient(_make_app(cron_token="secret-xyz"))
    response = client.post("/protected", headers={"X-Cron-Token": "secret-xyz"})
    assert response.status_code == 200
    assert response.json() == {"ok": True}
