from uuid import UUID

from pydantic import BaseModel, Field

from app.config import get_settings, Settings
from app.database import NodeModel
from app.schemas.jobs import Job
from app.services import JobsService

settings: Settings = get_settings()


class CreateNodeRequest(BaseModel):
    max_concurrent_jobs: int = Field(ge=0)
    max_total_jobs: int = Field(ge=0)


class Node(CreateNodeRequest):
    id: UUID
    jobs: list[Job] = []

    @classmethod
    def from_obj(cls, node_entity: NodeModel):
        return cls(
            id=node_entity.id,
            max_concurrent_jobs=node_entity.max_concurrent_jobs,
            max_total_jobs=node_entity.max_total_jobs,
            jobs=[Job.from_obj(JobsService.get_job(job_id)) for job_id in node_entity.jobs],
        )
