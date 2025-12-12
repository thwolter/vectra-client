# Client API

`VectraClient` wraps the HTTP requests and enforces tenant boundaries.

## Initialization

Create the client with a bearer token and `VectraClientSettings`. The headers and timeout are derived from the settings instance, and the client keeps the base URL trimmed of trailing slashes.

```python
settings = VectraClientSettings(base_url="https://vectra.example.com")
client = VectraClient("token", settings=settings)
```

## Methods

### `get_chunks(request: ChunkSearchRequest) -> list[tuple[Document, float]]`

- Calls `/api/v1/search/chunks` and validates the JSON body against `ChunkSearchResponse`.
- Returns a list of `(Document, score)` tuples where each `Document` carries the chunk text and metadata, and the score is cast to `float` for downstream sorting.

### `check_document(request: CheckDocumentRequest) -> dict[str, Any]`

- Hits `/api/v1/search/document-availability` and forwards the raw JSON response, raising `VectraDocumentNotFound` if a 404 identifies a missing artifact.

Internally, `_request_json` handles `get`/`post` dispatching, raises `VectraResponseError` for non-success responses, and wraps connection issues with `VectraClientError`.
