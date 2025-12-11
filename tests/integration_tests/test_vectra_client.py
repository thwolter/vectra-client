import os
from uuid import UUID

import httpx
import pytest

from vectra_client import VectraClient
from vectra_client.errors import VectraClientError, VectraResponseError

DEFAULT_TENANT_ID = UUID("ae579baf-91c2-4497-abf5-44867e06c7a1")
DEFAULT_DIGEST = "vI7EHYpQg6bnz2PsLviZVeneXbMs9iqDQyOgUjIhClc="


async def _ensure_vectra_available(base_url: str, timeout: float) -> None:
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=timeout) as client:
            response = await client.get("/healthz")
    except Exception as exc:
        pytest.skip(f"Vectra API unavailable: {exc}")
    if response.status_code != 200:
        pytest.skip(f"Vectra health endpoint returned {response.status_code}")


async def test_vectra_client_search_chunks_against_live_api():
    base_url = os.getenv("VECTRA_API__BASE_URL")
    timeout_seconds = float(os.getenv("VECTRA_API__TIMEOUT", "10"))
    if not base_url:
        raise pytest.skip("VECTRA_API__BASE_URL not set")

    await _ensure_vectra_available(base_url, timeout_seconds)

    service_user_id = UUID(
        os.getenv("VECTRA_TEST_SERVICE_USER_ID", "00000000-0000-0000-0000-000000000000")
    )
    service_role = os.getenv("VECTRA_TEST_SERVICE_ROLE", "system")
    scopes_env = os.getenv("VECTRA_TEST_SERVICE_SCOPES", "")
    service_scopes = tuple(scope for scope in scopes_env.split(",") if scope)

    client = VectraClient(
        base_url=base_url,
        timeout_seconds=timeout_seconds,
        service_user_id=service_user_id,
        service_role=service_role,
        service_scopes=service_scopes,
    )

    tenant_id = UUID(os.getenv("VECTRA_TEST_TENANT_ID", str(DEFAULT_TENANT_ID)))
    limit = 2

    try:
        results = await client.search_chunks(
            tenant_id=tenant_id,
            collection="default",
            digest=DEFAULT_DIGEST,
            query="profit",
            limit=limit,
        )
    except VectraResponseError as exc:
        if exc.status_code and exc.status_code >= 500:
            pytest.skip(f"Vectra backend returned {exc.status_code}: {exc}")
        raise
    except VectraClientError as exc:
        pytest.skip(f"Vectra client unavailable: {exc}")

    assert len(results) <= limit
    for doc, score in results:
        assert doc.page_content
        assert isinstance(score, float)
