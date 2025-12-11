from uuid import UUID

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Endpoints(BaseSettings):
    get_chunks: str = "/api/v1/search/chunks"


class VectraClientSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
    )

    base_url: str | None = None
    get_chunks: str = "/api/v1/search/chunks"
    document_availability_endpoint: str = "/api/v1/search/document-availability"

    endpoints: Endpoints = Endpoints()

    timeout_seconds: float = Field(default=10.0, gt=0.0)
    service_user_id: UUID = UUID("00000000-0000-0000-0000-000000000000")
    service_role: str = "system"
    service_scopes: tuple[str, ...] = ()

    @field_validator("base_url", mode="after")
    @classmethod
    def validate_base_url(cls, value: str | None):
        if not value:
            raise ValueError("base_url must be set")
        return value.rstrip("/")

    def get_url(self, endpoint: str) -> str | None:
        if not self.base_url:
            return None
        return f"{self.base_url}{endpoint}"
