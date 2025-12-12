# Schema Reference

## ChunkMatch

| Field | Description |
| --- | --- |
| `chunk_id` | Optional chunk identifier returned by the backend. If present it's copied into the document metadata. |
| `text` | The chunk text. |
| `metadata` | Arbitrary metadata dictionary returned by the server. |
| `score` | Similarity score (converted to `float` before it escapes the client). |

## ChunkSearchResponse

Wraps the `results` list returned by the `/search/chunks` endpoint. Each entry is validated as a `ChunkMatch`.

## ChunkSearchRequest

| Field | Description |
| --- | --- |
| `query` | The search string. |
| `digest` | 32-byte SHA256 digest encoded as Base64 (see `SHA256B64` in `types.py`). |
| `collection` | Collection name (defaults to `default`, 1–255 characters). |
| `limit` | Maximum number of matches (1–64, default 10). |
| `metadata_filter` | Optional dict to filter chunks by metadata keys/values. |
| `exclude_chunk_ids` | Chunk IDs or indexes to skip from the result set. |
| `score_threshold` | Minimum acceptable similarity score. |

## CheckDocumentRequest

| Field | Description |
| --- | --- |
| `document_id` | UUID of the document you want to verify. |
| `digest` | Alternative digest identifier (same format as `ChunkSearchRequest.digest`). |
| `collection` | Collection name (defaults to `default`). |
