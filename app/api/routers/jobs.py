from uuid import UUID

from fastapi import APIRouter, status

from app.config import get_settings, Settings
from app.schemas.jobs import CreateJobRequest, Job
from app.services import JobsService

settings: Settings = get_settings()
router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}/jobs",
    tags=["Jobs"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[Job],
)
async def get_all_jobs() -> list[Job]:
    all_jobs = await JobsService.get_all_jobs()
    return [Job.from_obj(job) for job in all_jobs]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=list[Job],
)
async def submit_jobs(jobs: list[CreateJobRequest]) -> list[Job]:
    job_entities = await JobsService.submit_jobs(jobs)
    return [Job.from_obj(job) for job in job_entities]


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def terminate_job(job_id: UUID) -> None:
    await JobsService.terminate_job(job_id)
