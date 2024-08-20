from uuid import UUID

from pydantic import BaseModel, Field

from app.config import get_settings, Settings
from app.schemas.jobs import Job

settings: Settings = get_settings()


class CreateNodeRequest(BaseModel):
    max_concurrent_jobs: int = Field(ge=0)
    max_total_jobs: int = Field(ge=0)


class Node(CreateNodeRequest):
    id: UUID
    jobs: list[Job] = []
