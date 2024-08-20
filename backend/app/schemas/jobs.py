from uuid import UUID

from pydantic import BaseModel

from app.config import get_settings, Settings
from app.utils.enums.jobs import JobStatus

settings: Settings = get_settings()


class CreateJobRequest(BaseModel):
    total_run_time: int  # milliseconds
    status: JobStatus = JobStatus.SCHEDULED


class Job(CreateJobRequest):
    id: UUID
    node_uuid: UUID
