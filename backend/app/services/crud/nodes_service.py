import uuid
from abc import ABC, abstractmethod
from uuid import UUID

from app.database import NodeModel, state
from app.schemas.nodes import CreateNodeRequest


class BaseNodesService(ABC):
    @staticmethod
    @abstractmethod
    def get_all_nodes() -> list[NodeModel]:
        pass

    @staticmethod
    @abstractmethod
    async def provision_nodes(nodes: list[CreateNodeRequest]) -> list[NodeModel]:
        pass

    @staticmethod
    @abstractmethod
    async def remove_node(node_id: UUID) -> None:
        pass


class InMemoryNodesService(BaseNodesService):
    @staticmethod
    def get_all_nodes() -> list[NodeModel]:
        return list(state["nodes"].values())

    @staticmethod
    async def provision_nodes(nodes: list[CreateNodeRequest]) -> list[NodeModel]:
        node_entities = []
        for node in nodes:
            node_id = uuid.uuid4()
            node_entity = NodeModel(
                id=node_id,
                max_concurrent_jobs=node.max_concurrent_jobs,
                max_total_jobs=node.max_total_jobs,
                jobs=[],
                metadata={"threads": [[] for _ in range(node.max_concurrent_jobs)]},
            )

            node_entities.append(node_entity)
            state["nodes"][node_id] = node_entity

        return node_entities

    @staticmethod
    async def remove_node(node_id: UUID) -> None:
        del state["nodes"][node_id]
