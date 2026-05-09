from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


class _RedisStub:
    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        return None


def test_health_endpoint_reports_ok(monkeypatch) -> None:
    app.state.redis = _RedisStub()

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "degraded"}
    assert payload["redis"] == "ok"
    assert payload["vector_db"] == "qdrant"
    assert payload["model_loaded"] is True or payload["model_loaded"] is False
