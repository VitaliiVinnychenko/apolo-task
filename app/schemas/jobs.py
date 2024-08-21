from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.config import get_settings, Settings
from app.database import JobModel
from app.utils.enums.jobs import JobStatus

settings: Settings = get_settings()


class CreateJobRequest(BaseModel):
    total_run_time: int = Field(ge=1)  # milliseconds


class Job(CreateJobRequest):
    id: UUID
    node_id: Optional[UUID]
    node_thread_id: Optional[int]
    expected_to_start_at: datetime
    expected_to_finish_at: datetime
    status: JobStatus = JobStatus.SCHEDULED

    @classmethod
    def from_obj(cls, job_entity: JobModel):
        return cls(
            id=job_entity.id,
            total_run_time=job_entity.total_run_time,
            node_id=job_entity.node_id,
            node_thread_id=job_entity.node_thread_id,
            status=job_entity.status,
            expected_to_start_at=job_entity.expected_to_start_at,
            expected_to_finish_at=job_entity.expected_to_finish_at,
        )
