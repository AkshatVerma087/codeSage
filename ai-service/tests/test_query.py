from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
import app.api.query as query_module


class _RedisStub:
    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        return None


class _Point:
    def __init__(self, payload: dict[str, object], score: float = 0.91) -> None:
        self.payload = payload
        self.score = score


class _EmbedderStub:
    def __init__(self) -> None:
        self.embedding_dim = 3
        self.encoder = self

    def encode_query(self, question: str):
        return [0.1, 0.2, 0.3]


class _VectorStoreStub:
    def __init__(self, embedding_dim: int) -> None:
        self.embedding_dim = embedding_dim

    async def query_async(self, collection_name: str, query_embedding, top_k: int = 6):
        return [
            _Point(
                {
                    "file_path": "src/app.py",
                    "start_line": 1,
                    "end_line": 12,
                    "symbol_name": "main",
                    "text": "def main():\n    return 'ok'",
                }
            )
        ]


class _LLMGeneratorStub:
    def generate(
        self,
        question: str,
        context: str,
        system_prompt=None,
        max_new_tokens: int = 256,
        temperature: float = 0.2,
    ) -> str:
        return f"answer:{question}:{context.splitlines()[0]}"


def test_query_endpoint_returns_contextual_answer(monkeypatch) -> None:
    app.state.redis = _RedisStub()
    monkeypatch.setattr(query_module, "Embedder", _EmbedderStub)
    monkeypatch.setattr(query_module, "VectorStore", _VectorStoreStub)
    monkeypatch.setattr(query_module, "LLMGenerator", _LLMGeneratorStub)

    async def _allow_all(redis, api_key):
        return True

    monkeypatch.setattr(query_module, "enforce_rate_limit", _allow_all)

    client = TestClient(app)
    response = client.post(
        "/v1/query",
        headers={"X-API-Key": query_module.settings.secret_key},
        json={
            "repo_id": "demo-repo",
            "question": "What does main do?",
            "top_k": 1,
            "max_new_tokens": 32,
            "temperature": 0.1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["repo_id"] == "demo-repo"
    assert payload["answer"].startswith("answer:What does main do?")
    assert payload["sources"][0]["file_path"] == "src/app.py"
