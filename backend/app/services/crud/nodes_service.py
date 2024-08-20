from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.nodes import Node, CreateNodeRequest


class BaseNodesService(ABC):

    @staticmethod
    @abstractmethod
    async def get_all_nodes() -> list[Node]:
        pass

    @staticmethod
    @abstractmethod
    async def provision_nodes(nodes: list[CreateNodeRequest]) -> list[Node]:
        pass

    @staticmethod
    @abstractmethod
    async def remove_node(node_id: UUID) -> None:
        pass


class InMemoryNodesService(BaseNodesService):

    @staticmethod
    async def get_all_nodes() -> list[Node]:
        pass

    @staticmethod
    async def provision_nodes(nodes: list[CreateNodeRequest]) -> list[Node]:
        pass

    @staticmethod
    async def remove_node(node_id: UUID) -> None:
        pass
