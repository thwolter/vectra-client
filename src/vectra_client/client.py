from typing import Any, Mapping, Sequence
from uuid import UUID

import httpx
from langchain_core.documents import Document
from pydantic import BaseModel, Field, ValidationError
from tenauth.schemas import AuthContext
from tenauth.utils import create_bearer_token

from .errors import VectraClientError, VectraResponseError
from .settings import VectraClientSettings


class _ChunkMatch(BaseModel):
    chunk_id: str | None = None
    text: str = Field(alias="text")
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float


class _ChunkSearchResponse(BaseModel):
    results: list[_ChunkMatch] = Field(default_factory=list)


class VectraClient:
    """HTTP client for querying document chunks in a tenant-aware Vectra backend."""

    def __init__(self, settings: VectraClientSettings) -> None:
        self._base_url = settings.base_url
        self._endpoint = settings.get_chunks
        self._document_availability_endpoint = settings.document_availability_endpoint
        self._timeout = settings.timeout_seconds
        self._service_user_id = settings.service_user_id
        self._service_role = settings.service_role
        self._service_scopes = settings.service_scopes

    def _build_headers(self, tenant_id: UUID) -> dict[str, str]:
        auth_ctx = AuthContext(
            sub=self._service_user_id,
            tid=tenant_id,
            role=self._service_role,
            scopes=list(self._service_scopes) or None,
        )
        token = create_bearer_token(auth_ctx)
        return {
            "Authorization": token,
            "X-Tenant-Id": str(tenant_id),
            "X-Tenant-User": str(self._service_user_id),
        }

    async def _request_json(
        self,
        *,
        path: str,
        payload: Mapping[str, Any],
        tenant_id: UUID,
    ) -> dict[str, Any]:
        payload_dict = dict(payload)
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url, timeout=self._timeout
            ) as client:
                response = await client.post(
                    path, json=payload_dict, headers=self._build_headers(tenant_id)
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text.strip() or exc.response.reason_phrase
            message = f"Vectra request to {path} failed with HTTP {exc.response.status_code}: {detail}"
            raise VectraResponseError(
                message, status_code=exc.response.status_code
            ) from exc
        except httpx.RequestError as exc:
            message = f"Failed to call Vectra backend: {exc}"
            raise VectraClientError(message) from exc

        try:
            return response.json()
        except ValueError as exc:  # pragma: no cover - defensive
            raise VectraResponseError(
                "Vectra response did not contain valid JSON"
            ) from exc

    async def search_chunks(
        self,
        *,
        tenant_id: UUID,
        collection: str,
        digest: str,
        query: str,
        limit: int,
        metadata_filter: Mapping[str, Any] | None = None,
        exclude_chunk_ids: Sequence[int | str] | None = None,
        score_threshold: float | None = None,
    ) -> list[tuple[Document, float]]:
        payload: dict[str, Any] = {
            "collection": collection,
            "digest": digest,
            "query": query,
            "limit": int(limit),
        }
        if metadata_filter:
            payload["metadata_filter"] = dict(metadata_filter)
        if exclude_chunk_ids:
            payload["exclude_chunk_ids"] = list(exclude_chunk_ids)
        if score_threshold is not None:
            payload["score_threshold"] = float(score_threshold)

        data = await self._request_json(
            path=self._endpoint, payload=payload, tenant_id=tenant_id
        )

        try:
            parsed = _ChunkSearchResponse.model_validate(data)
        except ValidationError as exc:
            raise VectraResponseError(
                "Vectra response payload could not be parsed"
            ) from exc

        results: list[tuple[Document, float]] = []
        for match in parsed.results:
            metadata = dict(match.metadata)
            if match.chunk_id is not None:
                metadata.setdefault("chunk_id", match.chunk_id)
            results.append(
                (
                    Document(page_content=match.text, metadata=metadata),
                    float(match.score),
                )
            )
        return results

    async def check_document_availability(
        self,
        *,
        tenant_id: UUID,
        collection: str,
        document_id: UUID | None = None,
        digest: str | None = None,
    ) -> dict[str, Any]:
        """Confirm the requested document exists for the tenant."""
        payload: dict[str, Any] = {"collection": collection}
        if document_id is not None:
            payload["document_id"] = str(document_id)
        if digest is not None:
            payload["digest"] = digest
        return await self._request_json(
            path=self._document_availability_endpoint,
            payload=payload,
            tenant_id=tenant_id,
        )


_default_client: VectraClient | None = None


def _build_client(settings: VectraClientSettings) -> VectraClient:
    if not settings.base_url:
        raise RuntimeError("base_url must be set for the Vectra client")
    return VectraClient(
        base_url=settings.base_url,
        endpoint=settings.get_chunks,
        document_availability_endpoint=settings.document_availability_endpoint,
        timeout_seconds=settings.timeout_seconds,
        service_user_id=settings.service_user_id,
        service_role=settings.service_role,
        service_scopes=settings.service_scopes,
    )


def get_vectra_client(
    settings: VectraClientSettings | type[VectraClientSettings] | None = None,
) -> VectraClient:
    """
    Return a client that is configured via the provided settings subclass or instance.

    When no settings are supplied the shared default settings are used and cached.
    """
    global _default_client

    if isinstance(settings, type):
        settings = settings()

    actual_settings = settings or VectraClientSettings()

    if settings is None and _default_client is not None:
        return _default_client

    client = _build_client(actual_settings)
    if settings is None:
        _default_client = client
    return client
