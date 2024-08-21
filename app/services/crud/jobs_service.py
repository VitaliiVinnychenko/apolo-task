import uuid
from abc import ABC, abstractmethod
from uuid import UUID

from app.database import JobModel, state
from app.schemas.jobs import CreateJobRequest
from app.services.jobs_scheduler import JobsScheduler
from app.utils.custom_exceptions import (
    JobAlreadyTerminatedOrDoneException,
    NoAvailableNodesLeftException,
)
from app.utils.enums.jobs import JobStatus


class BaseJobsService(ABC):
    @staticmethod
    @abstractmethod
    async def get_all_jobs():
        pass

    @staticmethod
    @abstractmethod
    def get_job(job_id: UUID):
        pass

    @staticmethod
    @abstractmethod
    async def submit_jobs(jobs: list[CreateJobRequest]):
        pass

    @staticmethod
    @abstractmethod
    async def terminate_job(job_id: UUID) -> None:
        pass


class InMemoryJobsService(BaseJobsService):
    @staticmethod
    async def get_all_jobs() -> list[JobModel]:
        await JobsScheduler.update_jobs(state)
        return list(state["jobs"].values())

    @staticmethod
    def get_job(job_id: UUID) -> JobModel:
        return state["jobs"][job_id]

    @staticmethod
    async def revert_jobs(job_entities: list[JobModel]):
        jobs_to_remove: list[UUID] = []

        # terminate jobs from the batch that were submitted before the node run out of resources
        for obj in job_entities:
            state["jobs"][obj.id].status = JobStatus.TERMINATED

        # update the jobs data and available node resources metrics
        await JobsScheduler.update_jobs(state)

        # delete all jobs from batch since they shouldn't have been
        # scheduled because of lack of available resources
        for obj in job_entities:
            jobs_to_remove.append(obj.id)
            del state["jobs"][obj.id]

        # remove deleted job ids from node entity's data
        for node_id in state["nodes"].keys():
            state["nodes"][node_id].jobs = [i for i in state["nodes"][node_id].jobs if i not in jobs_to_remove]

    @classmethod
    async def submit_jobs(cls, jobs: list[CreateJobRequest]) -> list[JobModel]:
        await JobsScheduler.update_jobs(state)
        jobs.sort(key=lambda obj: obj.total_run_time, reverse=True)

        job_entities = []
        for job in jobs:
            job_id = uuid.uuid4()
            job_entity = JobModel(
                id=job_id,
                total_run_time=job.total_run_time,
                status=JobStatus.SCHEDULED,
            )

            job_entities.append(job_entity)
            state["jobs"][job_id] = job_entity
            try:
                await JobsScheduler.schedule_job(state, job_id)
            except NoAvailableNodesLeftException as e:
                await cls.revert_jobs(job_entities)
                raise e

        return job_entities

    @staticmethod
    async def terminate_job(job_id: UUID) -> None:
        await JobsScheduler.update_jobs(state)
        if state["jobs"][job_id].status in (JobStatus.RUNNING, JobStatus.SCHEDULED):
            previous_status = state["jobs"][job_id].status
            state["jobs"][job_id].status = JobStatus.TERMINATED
            await JobsScheduler.handle_job_termination(state, job_id, previous_status)
        else:
            raise JobAlreadyTerminatedOrDoneException
