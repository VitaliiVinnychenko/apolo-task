from uuid import UUID

from fastapi import APIRouter, status

from app.services import JobsService
from app.config import get_settings, Settings
from app.schemas.jobs import CreateJobRequest, Job

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
    return await JobsService.get_all_jobs()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=list[Job],
)
async def submit_jobs(jobs: list[CreateJobRequest]) -> list[Job]:
    return await JobsService.submit_jobs(jobs)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def terminate_job(job_id: UUID) -> None:
    await JobsService.terminate_job(job_id)
