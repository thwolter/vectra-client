from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class VectraClientSettings(BaseSettings):
    base_url: str | None = None
    timeout_seconds: float = Field(default=10.0, gt=0.0)

    @field_validator("base_url", mode="after")
    @classmethod
    def validate_base_url(cls, value: str | None):
        if not value:
            raise ValueError("base_url must be set")
        return value.rstrip("/")
