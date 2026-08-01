from fastapi.testclient import TestClient

from app.main import create_app


def test_health() -> None:
    client = TestClient(create_app())
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_version() -> None:
    client = TestClient(create_app())
    res = client.get("/api/v1/version")
    assert res.status_code == 200
    assert "version" in res.json()
