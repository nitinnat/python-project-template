"""
Graph service for Neo4j operations.

Handles graph-based business logic.
"""

from typing import List, Optional

from neo4j import AsyncSession

from app.repositories.graph_repository import GraphRepository
from app.schemas.graph import (
    NodeCreate,
    NodeResponse,
    RelationshipCreate,
    RelationshipResponse,
    PathResponse,
)


class GraphService:
    """Service for graph operations."""

    def __init__(self, session: AsyncSession):
        self.repository = GraphRepository(session)

    async def create_node(self, node: NodeCreate) -> NodeResponse:
        """Create a node."""
        node_dict = await self.repository.create_node(node)
        return NodeResponse(**node_dict)

    async def get_node(self, node_id: str) -> Optional[NodeResponse]:
        """Get node by ID."""
        node = await self.repository.get_node(node_id)
        return NodeResponse(**node) if node else None

    async def create_relationship(
        self,
        relationship: RelationshipCreate,
    ) -> RelationshipResponse:
        """Create a relationship."""
        rel_dict = await self.repository.create_relationship(relationship)
        return RelationshipResponse(**rel_dict)

    async def find_path(
        self,
        from_node_id: str,
        to_node_id: str,
        max_depth: int = 5,
    ) -> Optional[PathResponse]:
        """
        Find shortest path between nodes.

        Args:
            from_node_id: Start node
            to_node_id: End node
            max_depth: Maximum path length

        Returns:
            Path or None
        """
        path = await self.repository.find_shortest_path(
            from_node_id,
            to_node_id,
            max_depth,
        )

        if not path:
            return None

        return PathResponse(
            nodes=[NodeResponse(**n) for n in path["nodes"]],
            relationships=[RelationshipResponse(**r) for r in path["relationships"]],
            length=path["length"],
        )

    async def get_neighbors(
        self,
        node_id: str,
        relationship_types: Optional[List[str]] = None,
        direction: str = "both",
        depth: int = 1,
    ) -> dict:
        """Get neighboring nodes."""
        result = await self.repository.get_neighbors(
            node_id,
            relationship_types,
            direction,
            depth,
        )

        return {
            "center_id": result["center_id"],
            "neighbors": [NodeResponse(**n) for n in result.get("neighbors", [])],
            "total": len(result.get("neighbors", [])),
        }

    async def delete_node(self, node_id: str) -> bool:
        """Delete node."""
        return await self.repository.delete_node(node_id)

    async def execute_query(self, query: str, parameters: dict = None) -> list:
        """Execute custom Cypher query."""
        return await self.repository.execute_cypher(query, parameters)
