from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.config import get_settings
from app.utils.enums.jobs import JobStatus

settings = get_settings()


# =====================================
#            Models (kind of)
# =====================================
@dataclass
class JobModel:
    id: UUID
    total_run_time: int  # milliseconds
    node_id: UUID | None  # node the job is scheduled on
    status: JobStatus = JobStatus.SCHEDULED
    expected_to_start_at: datetime | None = None
    expected_to_finish_at: datetime | None = None


@dataclass
class NodeModel:
    id: UUID
    max_concurrent_jobs: int
    max_total_jobs: int
    jobs: list[UUID]  # uuids of the jobs

    #  The threads and how jobs are distributed between them is stored medatata.
    #  Example:
    #  - the Node can run 3 jobs concurrently
    #
    #  metadata={
    #    "threads": [
    #       [],  - thread #1
    #       [],  - thread #2
    #       [],  - thread #3
    #    ],
    #  }
    metadata: dict


# =====================================
# The imitation of the database storage
# =====================================
state: dict[str, dict[UUID, NodeModel | JobModel]] = {"nodes": {}, "jobs": {}}
