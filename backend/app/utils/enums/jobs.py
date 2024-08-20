from enum import Enum


class JobStatus(str, Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    TERMINATED = "terminated"
    DONE = "done"
