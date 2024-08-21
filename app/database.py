from dataclasses import dataclass
from datetime import datetime
from typing import Optional
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
    node_id: Optional[UUID] = None  # node the job is scheduled on
    node_thread_id: Optional[int] = None
    expected_to_start_at: Optional[datetime] = None
    expected_to_finish_at: Optional[datetime] = None
    status: JobStatus = JobStatus.SCHEDULED


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
    #    "threads": [                       - pool of threads
    #       [],                             - thread #1
    #       [],                             - thread #2
    #       [],                             - thread #3
    #    ],
    #    "total_active_jobs": int,          - all jobs with the 'SCHEDULED' and 'RUNNING' statuses
    #    "free_threads": int,               - number of free threads (no jobs or already finished/terminated ones)
    #    "best_fit_thread": {               - the closest to be available thread info
    #       "thread_id": int                - id of the thread
    #       "available_at": datetime        - time when the thread is going to be free
    #    },
    #  }
    metadata: dict


# =====================================
# The imitation of the database storage
# =====================================
StateType = dict[str, dict[UUID, NodeModel | JobModel]]
state: StateType = {"nodes": {}, "jobs": {}}
