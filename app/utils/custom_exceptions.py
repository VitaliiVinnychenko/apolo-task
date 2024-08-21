from fastapi import HTTPException, status


class NoAvailableNodesLeftException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No available nodes left or not enough resources to run a batch of jobs. Please try later.",
        )


class JobAlreadyTerminatedOrDoneException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The job is already terminated or done.",
        )
