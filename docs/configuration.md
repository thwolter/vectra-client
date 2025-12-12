# Configuration

`VectraClientSettings` inherits from `pydantic_settings.BaseSettings`, so you can configure it via environment variables or direct instantiation. Two keys matter:

| Option | Description |
| --- | --- |
| `base_url` | Required base URL of the Vectra tenant. Trailing slashes are trimmed. Environment variables follow the field name (`BASE_URL` or `base_url` depending on your loader). |
| `timeout_seconds` | Request timeout with a default of `10.0` seconds. It must be positive; override it with `TIMEOUT_SECONDS` or by passing the value explicitly to the constructor. |

If you need to reuse the same client across your application, use the cached factory:

```python
from vectra_client.factory import get_vectra_client

client = get_vectra_client("token")
```

You can also subclass `VectraClientSettings` to add helpers or defaults and pass it via `settings_cls`:

```python
from vectra_client.factory import get_vectra_client
from vectra_client.settings import VectraClientSettings

class AwsSettings(VectraClientSettings):
    base_url: str = "https://vectra.us-east-1.internal"

client = get_vectra_client("token", settings_cls=AwsSettings)
```
