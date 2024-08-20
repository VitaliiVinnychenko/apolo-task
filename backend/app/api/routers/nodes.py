from uuid import UUID

from fastapi import APIRouter, status

from app.config import get_settings, Settings
from app.schemas.nodes import CreateNodeRequest, Node
from app.services import NodesService

settings: Settings = get_settings()
router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}/nodes",
    tags=["Nodes"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[Node],
)
async def get_all_nodes() -> list[Node]:
    return await NodesService.get_all_nodes()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=list[Node],
)
async def provision_new_nodes(nodes: list[CreateNodeRequest]) -> list[Node]:
    return await NodesService.provision_nodes(nodes)


@router.delete(
    "/{node_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_node(node_id: UUID) -> None:
    await NodesService.remove_node(node_id)
