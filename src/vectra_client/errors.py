class VectraClientError(RuntimeError):
    """Base exception raised when the Vectra client cannot satisfy a request."""

    pass


class VectraRouteNotFound(VectraClientError):
    pass


class VectraResponseError(VectraClientError):
    """Raised when the backend responds with a non-success status or invalid payload."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class VectraDocumentNotFound(VectraResponseError):
    pass
