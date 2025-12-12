# Usage

`VectraClient` is asynchronous and exposes two primary operations:

## Searching chunks

Prepare a `ChunkSearchRequest` with the query text, the expected digest for the tenant, and any filters that narrow the search. Results are returned as `langchain_core.documents.Document` objects paired with their similarity score.

```python
import asyncio
from langchain_core.documents import Document
from vectra_client.client import VectraClient
from vectra_client.schemas import ChunkSearchRequest
from vectra_client.settings import VectraClientSettings

async def search():
    settings = VectraClientSettings(base_url="https://vectra.example.com")
    client = VectraClient("api-token", settings=settings)

    request = ChunkSearchRequest(
        query="What is the status of the backup",
        digest="<your 32-byte SHA-256 base64 digest>",
        collection="logs",
        limit=5,
    )

    matches = await client.get_chunks(request)
    for document, score in matches:
        print(document.page_content)
        print("score", score)

asyncio.run(search())
```

## Checking document availability

`check_document` ensures a document is known to the tenant before you attempt a heavier workflow. It accepts either `document_id` or `digest` alongside the `collection`.

```python
from uuid import UUID
from vectra_client.schemas import CheckDocumentRequest

request = CheckDocumentRequest(document_id=UUID("5d2f-..."))
status = await client.check_document(request)
print(status)
```
