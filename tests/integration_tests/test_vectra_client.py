import os
import uuid
from uuid import UUID

import httpx
import pytest

from vectra_client.errors import VectraDocumentNotFound
from vectra_client.factory import get_vectra_client
from vectra_client.schemas import CheckDocumentRequest, ChunkSearchRequest

BASE_URL = "http://0.0.0.0:8000"
DEFAULT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMDFjYjg4MS0zYzMwLTRiYWUtYWQ3NC02MjU1YjBjMWVmZjkiLCJ0aWQiOiJhZTU3OWJhZi05MWMyLTQ0OTctYWJmNS00NDg2N2UwNmM3YTEiLCJyb2xlIjoiYWRtaW4iLCJwbGFuIjoiZGV2IiwiaWF0IjoxNzU5MTcwMjg2LCJleHAiOjE3NTkxNzM4ODYsImlzcyI6InZlY2FwaSIsImF1ZCI6InZlY2FwaS1jbGllbnRzIn0.N6uPB11ks-DbLKNpn9haUr_tVOP1t01k3_ni-fywcWc"  # gitleaks:allow
DEFAULT_DIGEST = "2/OjFFVI1DIA4dCoNRHXEracj6Rauhql/M/Ar8/HPI0="
DEFAULT_DOCUMENT_ID = UUID("af7b98d1-0713-4adf-8c45-8da8e84bb67b")


@pytest.fixture(scope="session", autouse=True)
def set_base_url():
    os.environ["BASE_URL"] = BASE_URL


@pytest.fixture(scope="session", autouse=True)
async def ensure_vectra_available():
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
            response = await client.get(BASE_URL + "/health/live")
    except Exception as exc:
        pytest.skip(f"Vectra API unavailable: {exc}")
    if response.status_code != 200:
        pytest.skip(f"Vectra health endpoint returned {response.status_code}")


async def test_vectra_client_search_chunks_against_live_api():
    client = get_vectra_client(DEFAULT_TOKEN)

    request = ChunkSearchRequest(
        digest=DEFAULT_DIGEST,
        query="Haidach",
        limit=2,
    )
    results = await client.get_chunks(request)

    assert len(results) <= 2
    assert len(results) > 0
    for doc, score in results:
        assert doc.page_content
        assert isinstance(score, float)


async def test_vectra_client_check_document_against_live_api():
    client = get_vectra_client(DEFAULT_TOKEN)

    request = CheckDocumentRequest(
        document_id=uuid.uuid4(),
        digest=DEFAULT_DIGEST,
    )

    with pytest.raises(VectraDocumentNotFound):
        await client.check_document(request)

    request = CheckDocumentRequest(
        document_id=DEFAULT_DOCUMENT_ID,
        digest=DEFAULT_DIGEST,
    )

    response = await client.check_document(request)
    assert len(response) > 0

    request = CheckDocumentRequest(
        digest=DEFAULT_DIGEST,
    )

    response = await client.check_document(request)
    assert len(response) > 0
