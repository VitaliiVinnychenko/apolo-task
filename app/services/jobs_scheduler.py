import asyncio
from collections import namedtuple
from datetime import datetime, timedelta
from uuid import UUID

from app.database import NodeModel, StateType
from app.logger import get_logger
from app.utils.custom_exceptions import NoAvailableNodesLeftException
from app.utils.enums.jobs import JobStatus

logger = get_logger(__name__)


class JobsScheduler:
    @staticmethod
    def _update_best_fit_thread_dict(node_entity: NodeModel, thread_id: int, available_at: datetime | None):
        node_entity.metadata["best_fit_thread"] = {
            "thread_id": thread_id,
            "available_at": available_at,  # 'None' means it can be used right away
        }
        logger.debug(
            "Best thread on node='%s' to schedule the job: %s", node_entity.id, node_entity.metadata["best_fit_thread"]
        )

    @classmethod
    async def refresh_threads_metadata(cls, state: StateType, node_id: UUID):
        node_entity = state["nodes"][node_id]

        if node_entity.metadata["free_threads"] == node_entity.max_concurrent_jobs:
            cls._update_best_fit_thread_dict(node_entity, 0, None)
        else:
            last_jobs_per_thread = []
            Thread = namedtuple("Thread", ["id", "available_at"])

            for thread_id in range(len(node_entity.metadata["threads"])):
                thread = node_entity.metadata["threads"][thread_id]
                if not thread:
                    cls._update_best_fit_thread_dict(node_entity, thread_id, None)
                    return

                last_jobs_per_thread.append(
                    Thread(
                        id=thread_id,
                        available_at=state["jobs"][thread[-1]].expected_to_finish_at,
                    )
                )

            last_jobs_per_thread.sort(key=lambda x: x.available_at)
            cls._update_best_fit_thread_dict(
                node_entity, last_jobs_per_thread[0].id, last_jobs_per_thread[0].available_at
            )

    @classmethod
    async def _remove_inactive_jobs(cls, state: StateType, node_id: UUID, inactive_jobs: list[UUID]):
        for thread_id in range(len(state["nodes"][node_id].metadata["threads"])):
            jobs_in_thread = len(state["nodes"][node_id].metadata["threads"][thread_id])
            state["nodes"][node_id].metadata["threads"][thread_id] = [
                i for i in state["nodes"][node_id].metadata["threads"][thread_id] if i not in inactive_jobs
            ]
            active_jobs_in_thread = len(state["nodes"][node_id].metadata["threads"][thread_id])
            state["nodes"][node_id].metadata["total_active_jobs"] -= jobs_in_thread - active_jobs_in_thread

            if not active_jobs_in_thread:
                state["nodes"][node_id].metadata["free_threads"] += 1

        await cls.refresh_threads_metadata(state, node_id)

    @staticmethod
    async def _update_job_status(state: StateType, job_id: UUID) -> UUID | None:
        if state["jobs"][job_id].status in (
            JobStatus.SCHEDULED,
            JobStatus.RUNNING,
        ):
            if (
                state["jobs"][job_id].expected_to_start_at
                <= datetime.now()
                < state["jobs"][job_id].expected_to_finish_at
            ):
                state["jobs"][job_id].status = JobStatus.RUNNING
            elif state["jobs"][job_id].expected_to_finish_at <= datetime.now():
                state["jobs"][job_id].status = JobStatus.DONE

        return job_id if state["jobs"][job_id].status in (JobStatus.DONE, JobStatus.TERMINATED) else None

    @classmethod
    async def update_jobs(cls, state: StateType):
        """
        Ideally the job status should be changed via callback once the job if finished
        but since it's an emulation of job schedulement and we do not have such option
        then it is done before each GET, POST or DELETE request.
        """
        inactive_jobs = await asyncio.gather(
            *[cls._update_job_status(state, job_id) for job_id in state["jobs"].keys()]
        )
        # remove all None elements
        inactive_jobs = [job_id for job_id in inactive_jobs if job_id]

        # Remove inactive jobs from all nodes threads and update metadata
        logger.info("Removing inactive jobs: %s", inactive_jobs)
        async with asyncio.TaskGroup() as tg:
            for node_id in state["nodes"].keys():
                tg.create_task(cls._remove_inactive_jobs(state, node_id, inactive_jobs))

        logger.debug(state)

    @staticmethod
    def _append_new_job_to_node(
        state: StateType,
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
        state["jobs"][job_id].node_thread_id = thread_id
        state["jobs"][job_id].expected_to_start_at = start_time
        state["jobs"][job_id].expected_to_finish_at = start_time + timedelta(
            milliseconds=state["jobs"][job_id].total_run_time
        )

    @classmethod
    async def schedule_job(cls, state: StateType, job_id: UUID):
        Node = namedtuple("Node", ["id", "thread_id", "available_at"])
        nodes_availability = []

        for node_id, node_entity in state["nodes"].items():
            if node_entity.metadata["total_active_jobs"] < node_entity.max_total_jobs:
                thread_id = node_entity.metadata["best_fit_thread"]["thread_id"]
                node_available_at = node_entity.metadata["best_fit_thread"]["available_at"]

                if not node_available_at:
                    cls._append_new_job_to_node(state, node_id, job_id, thread_id, node_available_at)
                    await cls.refresh_threads_metadata(state, node_id)
                    return

                nodes_availability.append(Node(node_id, thread_id, node_available_at))

        if not nodes_availability:
            raise NoAvailableNodesLeftException

        nodes_availability.sort(key=lambda x: x.available_at)
        node = nodes_availability[0]
        cls._append_new_job_to_node(state, node.id, job_id, node.thread_id, node.available_at)
        await cls.refresh_threads_metadata(state, node.id)

    @classmethod
    async def handle_job_termination(cls, state: StateType, job_id: UUID, previous_status: JobStatus):
        job_entity = state["jobs"][job_id]
        jobs_thread = state["nodes"][job_entity.node_id].metadata["threads"][job_entity.node_thread_id]
        job_index = jobs_thread.index(job_id)
        jobs_to_reschedule = jobs_thread[job_index + 1 :]
        remaining_jobs = jobs_thread[:job_index]

        logger.debug("Terminated job: %s", job_entity)
        logger.debug("Jobs to reschedule: %s", jobs_to_reschedule)

        if not jobs_to_reschedule:
            return

        if previous_status == JobStatus.RUNNING or not remaining_jobs:
            starting_point = datetime.now()
            new_status = JobStatus.RUNNING
        else:
            starting_point = remaining_jobs[-1].expected_to_finish_at
            new_status = JobStatus.SCHEDULED

        for job in jobs_to_reschedule:
            state["jobs"][job].expected_to_start_at = starting_point
            state["jobs"][job].expected_to_finish_at = starting_point + timedelta(
                milliseconds=state["jobs"][job].total_run_time
            )
            starting_point = state["jobs"][job].expected_to_finish_at

        state["jobs"][jobs_to_reschedule[0]].status = new_status
        state["nodes"][job_entity.node_id].metadata["threads"][job_entity.node_thread_id] = (
            remaining_jobs + jobs_to_reschedule
        )
        await cls.update_jobs(state)
        await cls.refresh_threads_metadata(state, job_entity.node_id)

    @classmethod
    async def handle_node_removal(cls):
        pass
