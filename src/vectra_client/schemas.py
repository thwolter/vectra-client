from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from .types import SHA256B64


class ChunkMatch(BaseModel):
    chunk_id: str | None = None
    text: str = Field(alias="text")
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float


class ChunkSearchResponse(BaseModel):
    results: list[ChunkMatch] = Field(default_factory=list)


class ChunkSearchRequest(BaseModel):
    query: str
    digest: SHA256B64
    collection: str = Field(default="default", min_length=1, max_length=255)
    limit: int = Field(default=10, ge=1, le=64)
    metadata_filter: dict[str, Any] | None = None
    exclude_chunk_ids: list[int | str] | None = None
    score_threshold: float | None = None


class CheckDocumentRequest(BaseModel):
    document_id: UUID | None = None
    digest: SHA256B64 | None = None
    collection: str = Field(default="default", min_length=1, max_length=255)
