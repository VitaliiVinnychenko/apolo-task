from fastapi import HTTPException, status


class NoAvailableNodesLeftException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No available nodes left to run a new batch of jobs. Please try later.",
        )
