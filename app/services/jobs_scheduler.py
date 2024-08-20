from collections import namedtuple
from datetime import datetime, timedelta
from uuid import UUID

from app.database import JobModel, NodeModel
from app.utils.enums.jobs import JobStatus


class JobsScheduler:
    @staticmethod
    def _update_best_fit_thread_dict(node_entity: NodeModel, thread_id: int, available_at: datetime | None):
        node_entity.metadata["best_fit_thread"] = {
            "thread_id": thread_id,
            "available_at": available_at,  # 'None' means it can be used right away
        }

    @classmethod
    def refresh_threads_metadata(cls, state: dict[str, dict[UUID, NodeModel | JobModel]], node_id: UUID):
        node_entity = state["nodes"][node_id]

        if node_entity.metadata["free_threads"] == node_entity.max_concurrent_jobs:
            cls._update_best_fit_thread_dict(node_entity, 0, None)
        else:
            last_jobs_per_thread = []
            Thread = namedtuple("Thread", ["id", "active_jobs", "available_at"])

            for thread_id in range(len(node_entity.metadata["threads"])):
                thread = node_entity.metadata["threads"][thread_id]
                jobs_amount = len(thread)
                if not jobs_amount:
                    cls._update_best_fit_thread_dict(node_entity, thread_id, None)
                    return

                last_jobs_per_thread.append(
                    Thread(
                        id=thread_id,
                        active_jobs=jobs_amount,
                        available_at=state["jobs"][thread[-1]].expected_to_finish_at,
                    )
                )

            last_jobs_per_thread.sort(
                key=lambda x: (
                    x.active_jobs,
                    x.available_at,
                )
            )
            cls._update_best_fit_thread_dict(
                node_entity, last_jobs_per_thread[0].id, last_jobs_per_thread[0].available_at
            )

    @classmethod
    async def update_jobs(cls, state: dict[str, dict[UUID, NodeModel | JobModel]]):
        inactive_jobs = []

        # Update job status in each job entity
        for job_id, job_entity in state["jobs"].items():
            if job_entity.status in (
                JobStatus.SCHEDULED,
                JobStatus.RUNNING,
            ):
                if job_entity.expected_to_start_at <= datetime.now() < job_entity.expected_to_finish_at:
                    job_entity.status = JobStatus.RUNNING
                elif datetime.now() <= job_entity.expected_to_finish_at:
                    job_entity.status = JobStatus.RUNNING

            if job_entity.status in (
                JobStatus.DONE,
                JobStatus.TERMINATED,
            ):
                inactive_jobs.append(job_id)

        # Remove inactive jobs from all nodes threads and update metadata
        for node_id, node_entity in state["nodes"].items():
            for thread_id in range(len(node_entity.metadata["threads"])):
                # TODO: use asyncio tasks here
                jobs_in_thread = len(node_entity.metadata["threads"][thread_id])
                node_entity.metadata["threads"][thread_id] = [
                    i for i in node_entity.metadata["threads"][thread_id] if i not in inactive_jobs
                ]
                active_jobs_in_thread = len(node_entity.metadata["threads"][thread_id])
                node_entity.metadata["total_active_jobs"] -= jobs_in_thread - active_jobs_in_thread

                if not active_jobs_in_thread:
                    node_entity.metadata["free_threads"] += 1

            cls.refresh_threads_metadata(state, node_id)

        print(state)

    @staticmethod
    def _append_new_job_to_node(
        state: dict[str, dict[UUID, NodeModel | JobModel]],
        node_id: UUID,
        job_id: UUID,
        thread_id: int,
        start_time: datetime | None,
    ):
        state["nodes"][node_id].jobs.append(job_id)
        state["nodes"][node_id].metadata["threads"][thread_id].append(job_id)
        state["nodes"][node_id].metadata["total_active_jobs"] += 1
        if not start_time:
            state["nodes"][node_id].metadata["free_threads"] -= 1
            start_time = datetime.now()

        # update job entity
        state["jobs"][job_id].node_id = node_id
        state["jobs"][job_id].expected_to_start_at = start_time
        state["jobs"][job_id].expected_to_finish_at = start_time + timedelta(
            milliseconds=state["jobs"][job_id].total_run_time
        )

    @classmethod
    async def schedule_job(cls, state: dict[str, dict[UUID, NodeModel | JobModel]], job_id: UUID):
        Node = namedtuple("Node", ["id", "thread_id", "available_at"])
        nodes_availability = []

        for node_id, node_entity in state["nodes"].items():
            if node_entity.metadata["total_active_jobs"] < node_entity.max_total_jobs:
                thread_id = node_entity.metadata["best_fit_thread"]["thread_id"]
                node_available_at = node_entity.metadata["best_fit_thread"]["available_at"]

                if not node_available_at:
                    cls._append_new_job_to_node(state, node_id, job_id, thread_id, node_available_at)
                    cls.refresh_threads_metadata(state, node_id)
                    return

                nodes_availability.append(Node(node_id, thread_id, node_available_at))

        nodes_availability.sort(key=lambda x: x.available_at)
        # TODO: handle unavailability of all nodes
        node = nodes_availability[0]
        cls._append_new_job_to_node(state, node.id, job_id, node.thread_id, node.available_at)
        cls.refresh_threads_metadata(state, node.id)
