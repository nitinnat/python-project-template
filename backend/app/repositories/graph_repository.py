"""
Graph repository for Neo4j operations.

Handles CRUD operations for nodes and relationships in Neo4j.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from neo4j import AsyncSession

from app.schemas.graph import NodeCreate, RelationshipCreate


class GraphRepository:
    """Repository for graph operations in Neo4j."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_node(self, node: NodeCreate) -> Dict[str, Any]:
        """
        Create a node in the graph.

        Args:
            node: Node data

        Returns:
            Created node with ID
        """
        query = """
        CREATE (n:Node {
            name: $name,
            node_type: $node_type,
            properties: $properties,
            created_at: datetime()
        })
        RETURN elementId(n) as id, n.name as name, n.node_type as node_type,
               n.properties as properties, n.created_at as created_at
        """

        result = await self.session.run(
            query,
            name=node.name,
            node_type=node.node_type,
            properties=node.properties,
        )

        record = await result.single()
        return dict(record) if record else None

    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get node by ID.

        Args:
            node_id: Node element ID

        Returns:
            Node data or None
        """
        query = """
        MATCH (n)
        WHERE elementId(n) = $node_id
        RETURN elementId(n) as id, n.name as name, n.node_type as node_type,
               n.properties as properties, n.created_at as created_at
        """

        result = await self.session.run(query, node_id=node_id)
        record = await result.single()
        return dict(record) if record else None

    async def create_relationship(
        self,
        relationship: RelationshipCreate,
    ) -> Dict[str, Any]:
        """
        Create a relationship between nodes.

        Args:
            relationship: Relationship data

        Returns:
            Created relationship
        """
        query = """
        MATCH (from)
        WHERE elementId(from) = $from_node_id
        MATCH (to)
        WHERE elementId(to) = $to_node_id
        CREATE (from)-[r:RELATIONSHIP {
            relationship_type: $relationship_type,
            properties: $properties,
            created_at: datetime()
        }]->(to)
        RETURN elementId(r) as id, r.relationship_type as relationship_type,
               r.properties as properties, r.created_at as created_at,
               elementId(from) as from_node_id, elementId(to) as to_node_id
        """

        result = await self.session.run(
            query,
            from_node_id=relationship.from_node_id,
            to_node_id=relationship.to_node_id,
            relationship_type=relationship.relationship_type,
            properties=relationship.properties,
        )

        record = await result.single()
        return dict(record) if record else None

    async def find_shortest_path(
        self,
        from_node_id: str,
        to_node_id: str,
        max_depth: int = 5,
    ) -> Optional[Dict[str, Any]]:
        """
        Find shortest path between two nodes.

        Args:
            from_node_id: Start node ID
            to_node_id: End node ID
            max_depth: Maximum path length

        Returns:
            Path information or None
        """
        query = """
        MATCH (from), (to)
        WHERE elementId(from) = $from_node_id AND elementId(to) = $to_node_id
        MATCH path = shortestPath((from)-[*..%d]-(to))
        RETURN [node IN nodes(path) | {
            id: elementId(node),
            name: node.name,
            node_type: node.node_type
        }] as nodes,
        [rel IN relationships(path) | {
            id: elementId(rel),
            type: type(rel)
        }] as relationships,
        length(path) as length
        """ % max_depth

        result = await self.session.run(
            query,
            from_node_id=from_node_id,
            to_node_id=to_node_id,
        )

        record = await result.single()
        return dict(record) if record else None

    async def get_neighbors(
        self,
        node_id: str,
        relationship_types: Optional[List[str]] = None,
        direction: str = "both",
        depth: int = 1,
    ) -> Dict[str, Any]:
        """
        Get neighboring nodes.

        Args:
            node_id: Center node ID
            relationship_types: Filter by relationship types
            direction: "incoming", "outgoing", or "both"
            depth: Traversal depth

        Returns:
            Neighbors and relationships
        """
        # Build relationship pattern based on direction
        if direction == "incoming":
            rel_pattern = "<-[r*1..%d]-" % depth
        elif direction == "outgoing":
            rel_pattern = "-[r*1..%d]->" % depth
        else:
            rel_pattern = "-[r*1..%d]-" % depth

        query = f"""
        MATCH (center)
        WHERE elementId(center) = $node_id
        MATCH (center){rel_pattern}(neighbor)
        RETURN elementId(center) as center_id,
               collect(DISTINCT {{
                   id: elementId(neighbor),
                   name: neighbor.name,
                   node_type: neighbor.node_type
               }}) as neighbors
        """

        result = await self.session.run(query, node_id=node_id)
        record = await result.single()

        if not record:
            return {"center_id": node_id, "neighbors": []}

        return dict(record)

    async def execute_cypher(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute custom Cypher query.

        Args:
            query: Cypher query
            parameters: Query parameters

        Returns:
            Query results
        """
        result = await self.session.run(query, **(parameters or {}))
        records = await result.values()
        return [dict(record) for record in records]

    async def delete_node(self, node_id: str) -> bool:
        """
        Delete node and its relationships.

        Args:
            node_id: Node ID to delete

        Returns:
            True if deleted
        """
        query = """
        MATCH (n)
        WHERE elementId(n) = $node_id
        DETACH DELETE n
        RETURN count(n) as deleted
        """

        result = await self.session.run(query, node_id=node_id)
        record = await result.single()
        return record and record["deleted"] > 0
