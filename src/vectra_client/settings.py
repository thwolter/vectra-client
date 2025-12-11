from uuid import UUID

from nexor.utils import ValidatedModel
from pydantic import Field


class VectraClientSettings(ValidatedModel):
    required_keys = ["base_url"]

    base_url: str | None = None
    endpoint: str = "/api/v1/search/chunks"
    document_availability_endpoint: str = "/api/v1/search/document-availability"
    timeout_seconds: float = Field(default=10.0, gt=0.0)
    service_user_id: UUID = UUID("00000000-0000-0000-0000-000000000000")
    service_role: str = "system"
    service_scopes: tuple[str, ...] = ()

    @property
    def retrieval_url(self) -> str | None:
        if not self.base_url:
            return None
        return f"{self.base_url}{self.endpoint}"
