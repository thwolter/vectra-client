from vectra_client import VectraClient, VectraClientSettings


def get_vectra_client(
    settings_cls: type[VectraClientSettings] | None = None,
) -> VectraClient:
    actual_settings = (settings_cls or VectraClientSettings)()
    return VectraClient(settings=actual_settings)
