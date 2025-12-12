# Error Types

| Exception | Description |
| --- | --- |
| `VectraClientError` | Base class for client failures such as connection errors. |
| `VectraRouteNotFound` | Reserved for future use when a backend route can't be resolved. |
| `VectraResponseError` | Raised when the backend responds with a non-success HTTP status or invalid payload. `status_code` is attached when available. |
| `VectraDocumentNotFound` | A specialized `VectraResponseError` raised when the backend explicitly reports `document_not_found`. |
