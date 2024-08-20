import uuid
from abc import ABC, abstractmethod
from uuid import UUID

from app.database import JobModel, state
from app.schemas.jobs import CreateJobRequest
from app.utils.enums.jobs import JobStatus


class BaseJobsService(ABC):
    @staticmethod
    @abstractmethod
    def get_all_jobs() -> list[JobModel]:
        pass

    @staticmethod
    @abstractmethod
    def get_job(job_id: UUID) -> JobModel:
        pass

    @staticmethod
    @abstractmethod
    async def submit_jobs(jobs: list[CreateJobRequest]) -> list[JobModel]:
        pass

    @staticmethod
    @abstractmethod
    async def terminate_job(job_id: UUID) -> None:
        pass


class InMemoryJobsService(BaseJobsService):
    @staticmethod
    def get_all_jobs() -> list[JobModel]:
        return list(state["jobs"].values())

    @staticmethod
    def get_job(job_id: UUID) -> JobModel:
        return state["jobs"][job_id]

    @staticmethod
    async def submit_jobs(jobs: list[CreateJobRequest]) -> list[JobModel]:
        job_entities = []
        for job in jobs:
            job_id = uuid.uuid4()
            job_entity = JobModel(
                id=job_id,
                total_run_time=job.total_run_time,
                status=JobStatus.SCHEDULED,
                node_id=None,
            )

            job_entities.append(job_entity)
            state["jobs"][job_id] = job_entity

        return job_entities

    @staticmethod
    async def terminate_job(job_id: UUID) -> None:
        del state["jobs"][job_id]
