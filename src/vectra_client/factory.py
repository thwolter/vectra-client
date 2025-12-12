from .client import VectraClient
from .settings import VectraClientSettings

_default_client: VectraClient | None = None


def get_vectra_client(
    token: str, *, settings_cls: type[VectraClientSettings] | None = None
) -> VectraClient:
    global _default_client

    if not _default_client:
        actual_settings = (settings_cls or VectraClientSettings)()
        _default_client = VectraClient(token, settings=actual_settings)

    return _default_client
