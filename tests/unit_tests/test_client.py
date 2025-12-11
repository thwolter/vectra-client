from __future__ import annotations

from uuid import uuid4

import pytest

from vectra_client import VectraClient


class _DummyResponse:
    def __init__(self, payload: dict):
        self._payload = payload
        self.status_code = 200
        self.text = ""
        self.reason_phrase = "OK"

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class _DummyAsyncClient:
    def __init__(self, *, base_url: str, timeout: float):
        self.base_url = base_url
        self.timeout = timeout
        self.last_path: str | None = None
        self.last_payload: dict | None = None
        self.last_headers: dict[str, str] | None = None
        self._response_map: dict[str, dict] = {
            "/api/v1/search/chunks": {
                "results": [
                    {
                        "chunk_id": "5",
                        "text": "chunk one",
                        "metadata": {"page": 1},
                        "score": 0.85,
                    }
                ]
            }
        }

    async def post(
        self, path: str, *, json: dict, headers: dict[str, str]
    ) -> _DummyResponse:
        self.last_path = path
        self.last_payload = json
        self.last_headers = headers
        return _DummyResponse(self._response_map.get(path, {}))

    async def __aenter__(self) -> "_DummyAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_vectra_client_builds_request_and_parses_response(monkeypatch):
    tenant_id = uuid4()
    service_user = uuid4()

    created_clients: list[_DummyAsyncClient] = []

    def _factory(**kwargs):
        client = _DummyAsyncClient(**kwargs)
        created_clients.append(client)
        return client

    monkeypatch.setattr("vectra_client.client.httpx.AsyncClient", _factory)

    client = VectraClient(
        base_url="http://vectra",
        timeout_seconds=5.0,
        service_user_id=service_user,
        service_role="system",
        service_scopes=("chunks:read",),
    )

    results = await client.search_chunks(
        tenant_id=tenant_id,
        collection="default",
        digest="digest",
        query="topic",
        limit=4,
        metadata_filter={"source": {"$eq": "file.pdf"}},
        exclude_chunk_ids=[1, 2],
        score_threshold=0.5,
    )

    assert len(results) == 1
    doc, score = results[0]
    assert doc.page_content == "chunk one"
    assert doc.metadata["chunk_id"] == "5"
    assert doc.metadata["page"] == 1
    assert score == 0.85

    assert created_clients
    sent = created_clients[0]
    assert sent.base_url == "http://vectra"
    assert sent.last_path == "/api/v1/search/chunks"
    assert sent.last_payload and sent.last_payload["collection"] == "default"
    assert sent.last_payload["metadata_filter"] == {"source": {"$eq": "file.pdf"}}
    assert sent.last_payload["exclude_chunk_ids"] == [1, 2]
    assert "Authorization" in (sent.last_headers or {})


@pytest.mark.asyncio
async def test_vectra_client_normalizes_base_url_and_endpoint(monkeypatch):
    tenant_id = uuid4()
    service_user = uuid4()

    created_clients: list[_DummyAsyncClient] = []

    def _factory(**kwargs):
        client = _DummyAsyncClient(**kwargs)
        created_clients.append(client)
        return client

    monkeypatch.setattr("vectra_client.client.httpx.AsyncClient", _factory)

    client = VectraClient(
        base_url="http://vectra/",
        endpoint="api/v1/search/chunks",
        timeout_seconds=5.0,
        service_user_id=service_user,
    )

    await client.search_chunks(
        tenant_id=tenant_id,
        collection="default",
        digest="digest",
        query="topic",
        limit=1,
    )

    assert created_clients
    sent = created_clients[0]
    assert sent.base_url == "http://vectra"
    assert sent.last_path == "/api/v1/search/chunks"


@pytest.mark.asyncio
async def test_vectra_client_checks_document_availability(monkeypatch):
    tenant_id = uuid4()
    service_user = uuid4()

    created_clients: list[_DummyAsyncClient] = []

    def _factory(**kwargs):
        client = _DummyAsyncClient(**kwargs)
        created_clients.append(client)
        return client

    monkeypatch.setattr("vectra_client.client.httpx.AsyncClient", _factory)

    client = VectraClient(
        base_url="http://vectra",
        timeout_seconds=5.0,
        service_user_id=service_user,
        document_availability_endpoint="api/v1/search/document-availability",
    )

    doc_id = uuid4()
    await client.check_document_availability(
        tenant_id=tenant_id,
        document_id=doc_id,
        digest="digest",
        collection="default",
    )

    assert created_clients
    sent = created_clients[0]
    assert sent.base_url == "http://vectra"
    assert sent.last_path == "/api/v1/search/document-availability"
    assert sent.last_payload and sent.last_payload["document_id"] == str(doc_id)
    assert sent.last_payload["digest"] == "digest"
    assert sent.last_payload["collection"] == "default"
