"""
Graph API endpoints.

Handles Neo4j graph operations.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from neo4j import AsyncSession

from app.api.deps import get_neo4j_session
from app.schemas.graph import (
    GraphQuery,
    NeighborsQuery,
    NeighborsResponse,
    NodeCreate,
    NodeResponse,
    PathQuery,
    PathResponse,
    RelationshipCreate,
    RelationshipResponse,
)
from app.services.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    node: NodeCreate,
    session: AsyncSession = Depends(get_neo4j_session),
):
    """
    Create a new node in the graph.

    Args:
        node: Node data
        session: Neo4j session

    Returns:
        Created node
    """
    service = GraphService(session)
    return await service.create_node(node)


@router.get("/nodes/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    session: AsyncSession = Depends(get_neo4j_session),
):
    """
    Get node by ID.

    Args:
        node_id: Node element ID
        session: Neo4j session

    Returns:
        Node data
    """
    service = GraphService(session)
    node = await service.get_node(node_id)

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )

    return node


@router.delete("/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    node_id: str,
    session: AsyncSession = Depends(get_neo4j_session),
):
    """
    Delete node and its relationships.

    Args:
        node_id: Node ID
        session: Neo4j session
    """
    service = GraphService(session)
    deleted = await service.delete_node(node_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )


@router.post(
    "/relationships",
    response_model=RelationshipResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_relationship(
    relationship: RelationshipCreate,
    session: AsyncSession = Depends(get_neo4j_session),
):
    """
    Create a relationship between nodes.

    Args:
        relationship: Relationship data
        session: Neo4j session

    Returns:
        Created relationship
    """
    service = GraphService(session)
    return await service.create_relationship(relationship)


@router.post("/path", response_model=Optional[PathResponse])
async def find_path(
    query: PathQuery,
    session: AsyncSession = Depends(get_neo4j_session),
):
    """
    Find shortest path between two nodes.

    Args:
        query: Path query with from/to nodes
        session: Neo4j session

    Returns:
        Path or None if no path exists
    """
    service = GraphService(session)
    return await service.find_path(
        query.from_node_id,
        query.to_node_id,
        query.max_depth,
    )


@router.post("/neighbors", response_model=NeighborsResponse)
async def get_neighbors(
    query: NeighborsQuery,
    session: AsyncSession = Depends(get_neo4j_session),
):
    """
    Get neighboring nodes.

    Args:
        query: Neighbors query
        session: Neo4j session

    Returns:
        Neighbors and relationships
    """
    service = GraphService(session)

    # Get center node
    center_node = await service.get_node(query.node_id)
    if not center_node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )

    # Get neighbors
    result = await service.get_neighbors(
        query.node_id,
        query.relationship_types,
        query.direction,
        query.depth,
    )

    return NeighborsResponse(
        center_node=center_node,
        neighbors=result["neighbors"],
        relationships=[],  # TODO: Include actual relationships
        total=result["total"],
    )


@router.post("/query")
async def execute_query(
    query: GraphQuery,
    session: AsyncSession = Depends(get_neo4j_session),
):
    """
    Execute custom Cypher query.

    Args:
        query: Cypher query and parameters
        session: Neo4j session

    Returns:
        Query results
    """
    service = GraphService(session)
    return await service.execute_query(query.query, query.parameters)
