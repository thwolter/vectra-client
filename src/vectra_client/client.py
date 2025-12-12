from typing import Any, Literal, Mapping, NoReturn

import httpx
from langchain_core.documents import Document
from pydantic import ValidationError

from .errors import VectraClientError, VectraDocumentNotFound, VectraResponseError
from .schemas import CheckDocumentRequest, ChunkSearchRequest, ChunkSearchResponse
from .settings import VectraClientSettings


def _raise_vectra_http_error(path: str, exc: httpx.HTTPStatusError) -> NoReturn:
    status = exc.response.status_code

    if status == 404:
        try:
            body = exc.response.json()
        except ValueError:
            body = {}

        detail = body.get("detail")
        if isinstance(detail, dict) and detail.get("error") == "document_not_found":
            raise VectraDocumentNotFound("Document not found", status_code=404) from exc

    detail_text = exc.response.text.strip() or exc.response.reason_phrase
    message = f"Vectra request to {path} failed with HTTP {status}: {detail_text}"
    raise VectraResponseError(message, status_code=status) from exc


class VectraClient:
    """HTTP client for querying document chunks in a tenant-aware Vectra backend."""

    @staticmethod
    def _build_headers(token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    def __init__(self, token: str, *, settings: VectraClientSettings) -> None:
        self._headers = self._build_headers(token)
        self._base_url = str(settings.base_url)
        self._timeout = settings.timeout_seconds

    async def _request_json(
        self,
        path: str,
        payload: Mapping[str, Any] | None = None,
        *,
        method: Literal["get", "post"] = "post",
    ) -> dict[str, Any]:
        payload_dict = dict(payload or {})
        request_method = method.lower()
        if request_method not in {"get", "post"}:
            raise ValueError("request method must be 'get' or 'post'")

        response: httpx.Response | None = None
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url, timeout=self._timeout
            ) as client:
                if request_method == "get":
                    response = await client.get(
                        path, params=payload_dict or None, headers=self._headers
                    )
                else:
                    response = await client.post(
                        path, json=payload_dict, headers=self._headers
                    )
                response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            _raise_vectra_http_error(path, exc)

        except httpx.RequestError as exc:
            message = f"Failed to call Vectra backend: {exc}"
            raise VectraClientError(message) from exc

        if response is None:
            raise VectraClientError("No response received from Vectra backend")

        try:
            return response.json()
        except ValueError as exc:  # pragma: no cover
            raise VectraResponseError(
                "Vectra response did not contain valid JSON"
            ) from exc

    async def get_chunks(
        self, request: ChunkSearchRequest
    ) -> list[tuple[Document, float]]:
        url = "/api/v1/search/chunks"
        data = await self._request_json(url, request.model_dump())

        try:
            parsed = ChunkSearchResponse.model_validate(data)
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

    async def check_document(self, request: CheckDocumentRequest) -> dict[str, Any]:
        """Confirm the requested document exists for the tenant."""
        url = "/api/v1/search/document-availability"
        return await self._request_json(url, request.model_dump(mode="json"))
