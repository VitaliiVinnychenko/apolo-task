from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.jobs import CreateJobRequest, Job


class BaseJobsService(ABC):
    @staticmethod
    @abstractmethod
    async def get_all_jobs() -> list[Job]:
        pass

    @staticmethod
    @abstractmethod
    async def submit_jobs(jobs: list[CreateJobRequest]) -> list[Job]:
        pass

    @staticmethod
    @abstractmethod
    async def terminate_job(job_id: UUID) -> None:
        pass


class InMemoryJobsService(BaseJobsService):
    @staticmethod
    async def get_all_jobs() -> list[Job]:
        pass

    @staticmethod
    async def submit_jobs(jobs: list[CreateJobRequest]) -> list[Job]:
        pass

    @staticmethod
    async def terminate_job(job_id: UUID) -> None:
        pass
