import copy
import uuid
from abc import ABC, abstractmethod
from uuid import UUID

from app.database import NodeModel, state
from app.schemas.nodes import CreateNodeRequest
from app.services.crud.jobs_service import InMemoryJobsService
from app.services.jobs_scheduler import JobsScheduler
from app.utils.custom_exceptions import NoAvailableNodesLeftException


class BaseNodesService(ABC):
    @staticmethod
    @abstractmethod
    async def get_all_nodes():
        pass

    @staticmethod
    @abstractmethod
    async def provision_nodes(nodes: list[CreateNodeRequest]):
        pass

    @staticmethod
    @abstractmethod
    async def remove_node(node_id: UUID) -> None:
        pass


class InMemoryNodesService(BaseNodesService):
    @staticmethod
    async def get_all_nodes() -> list[NodeModel]:
        await JobsScheduler.update_jobs(state)
        return list(state["nodes"].values())

    @staticmethod
    async def provision_nodes(nodes: list[CreateNodeRequest]) -> list[NodeModel]:
        await JobsScheduler.update_jobs(state)

        node_entities = []
        for node in nodes:
            node_id = uuid.uuid4()
            node_entity = NodeModel(
                id=node_id,
                max_concurrent_jobs=node.max_concurrent_jobs,
                max_total_jobs=node.max_total_jobs,
                vcpu_units=node.vcpu_units,
                memory=node.memory,
                jobs=[],
                metadata={
                    "threads": [set() for _ in range(node.max_concurrent_jobs)],
                    "free_threads": node.max_concurrent_jobs,
                    "total_active_jobs": 0,
                    "best_fit_thread": {
                        "thread_id": 0,
                        "available_at": None,  # 'None' means it can be used right away
                    },
                },
            )

            node_entities.append(node_entity)
            state["nodes"][node_id] = node_entity

        return node_entities

    @staticmethod
    async def remove_node(node_id: UUID) -> None:
        await JobsScheduler.update_jobs(state)

        previous_nodes_state = copy.deepcopy(state["nodes"])
        del state["nodes"][node_id]

        jobs_to_be_rescheduled = [
            job_id for thread in previous_nodes_state[node_id].metadata["threads"] for job_id in thread
        ]

        try:
            for job_id in jobs_to_be_rescheduled:
                await JobsScheduler.schedule_job(state, job_id)
        except NoAvailableNodesLeftException as e:
            state["nodes"] = previous_nodes_state
            raise e
