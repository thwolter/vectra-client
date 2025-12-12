# Vectra Client

A minimal shared client library for talking to the Vectra retrieval API. It hides the HTTP plumbing, applies tenant-aware validation, and converts chunk matches into `langchain_core` `Document`s so that downstream components can stay framework agnostic.

## What it covers

- **Search**: find chunked document text by `query`, `digest`, and optional metadata filters.
- **Document existence**: confirm that a particular document (or digest) lives within the configured collection before starting an expensive workflow.
- **Resilience**: translates HTTP failures into typed exceptions (`VectraResponseError`, `VectraDocumentNotFound`, etc.).

## Quick start

1. Install the project (see **Installation**) and ensure your runtime has Python 3.13 or newer.
2. Provide a bearer token and the base URL for the tenant.

```python
from vectra_client.client import VectraClient
from vectra_client.settings import VectraClientSettings

settings = VectraClientSettings(base_url="https://vectra.example.com")
client = VectraClient("your-token", settings=settings)
```

3. Build `ChunkSearchRequest` or `CheckDocumentRequest` objects (see the **Reference** section) and dispatch calls against the asynchronous API.
