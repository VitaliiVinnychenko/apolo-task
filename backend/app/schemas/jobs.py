from uuid import UUID

from pydantic import BaseModel

from app.config import get_settings, Settings
from app.database import JobModel
from app.utils.enums.jobs import JobStatus

settings: Settings = get_settings()


class CreateJobRequest(BaseModel):
    total_run_time: int  # milliseconds


class Job(CreateJobRequest):
    id: UUID
    node_uuid: UUID | None
    status: JobStatus = JobStatus.SCHEDULED

    @classmethod
    def from_obj(cls, job_entity: JobModel):
        return cls(
            id=job_entity.id,
            total_run_time=job_entity.total_run_time,
            node_uuid=job_entity.node_id,
            status=job_entity.status,
        )
