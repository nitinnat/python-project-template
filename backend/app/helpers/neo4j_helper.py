"""
Neo4j graph database helper using official driver.

Provides:
- Async driver support
- Cypher query execution
- Transaction management
- Graph algorithm wrappers
- Batch operations
"""

from typing import Any

from neo4j import AsyncGraphDatabase, AsyncDriver

from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Neo4jHelper:
    """
    Neo4j graph database helper using async driver.

    Implements singleton pattern for single driver instance.
    """

    _instance = None
    _driver: AsyncDriver | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self):
        """
        Initialize Neo4j driver.

        Called during application startup.
        """
        if self._driver is not None:
            logger.warning("Neo4j already initialized")
            return

        try:
            # Create async driver
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_url,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_pool_size=10,
            )

            # Test connection
            await self._driver.verify_connectivity()

            logger.info("Neo4j driver initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {e}")
            raise

    def get_session(self):
        """
        Get Neo4j session.

        Returns:
            Context manager for Neo4j session
        """
        if self._driver is None:
            raise RuntimeError("Neo4j driver not initialized")
        return self._driver.session()

    async def close(self):
        """
        Close Neo4j driver.

        Called during application shutdown.
        """
        if self._driver is None:
            return

        try:
            await self._driver.close()
            logger.info("Neo4j driver closed")
        except Exception as e:
            logger.error(f"Error closing Neo4j driver: {e}")
        finally:
            self._driver = None

    def get_driver(self) -> AsyncDriver:
        """
        Get Neo4j driver.

        Returns:
            AsyncDriver instance

        Raises:
            RuntimeError: If Neo4j not initialized
        """
        if self._driver is None:
            raise RuntimeError("Neo4j not initialized. Call initialize() first.")
        return self._driver

    async def execute_query(
        self,
        query: str,
        parameters: dict | None = None,
        database: str | None = None,
    ) -> list[dict]:
        """
        Execute Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters (optional)
            database: Database name (optional, uses default if None)

        Returns:
            List of result records as dictionaries

        Usage:
            results = await neo4j_helper.execute_query(
                "MATCH (n:Person {name: $name}) RETURN n",
                {"name": "Alice"}
            )
        """
        driver = self.get_driver()

        async with driver.session(database=database) as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def execute_write(
        self,
        query: str,
        parameters: dict | None = None,
        database: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute write query in a transaction.

        Args:
            query: Cypher query string
            parameters: Query parameters (optional)
            database: Database name (optional)

        Returns:
            Query statistics and metadata

        Usage:
            result = await neo4j_helper.execute_write(
                "CREATE (n:Person {name: $name}) RETURN n",
                {"name": "Bob"}
            )
        """
        driver = self.get_driver()

        async def _write_tx(tx):
            result = await tx.run(query, parameters or {})
            return await result.data()

        async with driver.session(database=database) as session:
            data = await session.execute_write(_write_tx)
            return {"data": data}

    async def create_node(
        self,
        label: str,
        properties: dict,
        database: str | None = None,
    ) -> dict:
        """
        Create a node with label and properties.

        Args:
            label: Node label
            properties: Node properties
            database: Database name (optional)

        Returns:
            Created node data

        Usage:
            node = await neo4j_helper.create_node(
                "Person",
                {"name": "Alice", "age": 30}
            )
        """
        # Build property string for Cypher
        props = ", ".join(f"{k}: ${k}" for k in properties.keys())
        query = f"CREATE (n:{label} {{{props}}}) RETURN n"

        result = await self.execute_write(query, properties, database)
        return result["data"][0] if result["data"] else {}

    async def find_nodes(
        self,
        label: str,
        properties: dict | None = None,
        limit: int | None = None,
        database: str | None = None,
    ) -> list[dict]:
        """
        Find nodes by label and optional properties.

        Args:
            label: Node label
            properties: Filter properties (optional)
            limit: Maximum number of results (optional)
            database: Database name (optional)

        Returns:
            List of matching nodes

        Usage:
            people = await neo4j_helper.find_nodes(
                "Person",
                {"age": 30},
                limit=10
            )
        """
        if properties:
            props = " AND ".join(f"n.{k} = ${k}" for k in properties.keys())
            query = f"MATCH (n:{label}) WHERE {props} RETURN n"
            if limit:
                query += f" LIMIT {limit}"
            params = properties
        else:
            query = f"MATCH (n:{label}) RETURN n"
            if limit:
                query += f" LIMIT {limit}"
            params = {}

        return await self.execute_query(query, params, database)

    async def create_relationship(
        self,
        from_label: str,
        from_props: dict,
        to_label: str,
        to_props: dict,
        relationship_type: str,
        relationship_props: dict | None = None,
        database: str | None = None,
    ) -> dict:
        """
        Create a relationship between two nodes.

        Args:
            from_label: Source node label
            from_props: Source node properties to match
            to_label: Target node label
            to_props: Target node properties to match
            relationship_type: Relationship type
            relationship_props: Relationship properties (optional)
            database: Database name (optional)

        Returns:
            Created relationship data

        Usage:
            rel = await neo4j_helper.create_relationship(
                "Person", {"name": "Alice"},
                "Person", {"name": "Bob"},
                "KNOWS",
                {"since": 2020}
            )
        """
        # Build match conditions
        from_match = " AND ".join(f"a.{k} = $from_{k}" for k in from_props.keys())
        to_match = " AND ".join(f"b.{k} = $to_{k}" for k in to_props.keys())

        # Build relationship properties
        if relationship_props:
            rel_props = ", ".join(
                f"{k}: $rel_{k}" for k in relationship_props.keys()
            )
            rel_create = f"-[r:{relationship_type} {{{rel_props}}}]->"
        else:
            rel_create = f"-[r:{relationship_type}]->"

        query = f"""
            MATCH (a:{from_label}), (b:{to_label})
            WHERE {from_match} AND {to_match}
            CREATE (a){rel_create}(b)
            RETURN r
        """

        # Combine all parameters
        params = {
            **{f"from_{k}": v for k, v in from_props.items()},
            **{f"to_{k}": v for k, v in to_props.items()},
        }
        if relationship_props:
            params.update({f"rel_{k}": v for k, v in relationship_props.items()})

        result = await self.execute_write(query, params, database)
        return result["data"][0] if result["data"] else {}

    async def shortest_path(
        self,
        from_label: str,
        from_props: dict,
        to_label: str,
        to_props: dict,
        relationship_type: str | None = None,
        max_depth: int = 5,
        database: str | None = None,
    ) -> list[dict]:
        """
        Find shortest path between two nodes.

        Args:
            from_label: Source node label
            from_props: Source node properties
            to_label: Target node label
            to_props: Target node properties
            relationship_type: Relationship type to traverse (optional)
            max_depth: Maximum path depth (default 5)
            database: Database name (optional)

        Returns:
            Shortest path as list of nodes and relationships

        Usage:
            path = await neo4j_helper.shortest_path(
                "Person", {"name": "Alice"},
                "Person", {"name": "Bob"},
                "KNOWS"
            )
        """
        from_match = " AND ".join(f"a.{k} = $from_{k}" for k in from_props.keys())
        to_match = " AND ".join(f"b.{k} = $to_{k}" for k in to_props.keys())

        if relationship_type:
            rel = f"[:{relationship_type}*1..{max_depth}]"
        else:
            rel = f"[*1..{max_depth}]"

        query = f"""
            MATCH (a:{from_label}), (b:{to_label}),
                  p = shortestPath((a){rel}(b))
            WHERE {from_match} AND {to_match}
            RETURN p
        """

        params = {
            **{f"from_{k}": v for k, v in from_props.items()},
            **{f"to_{k}": v for k, v in to_props.items()},
        }

        return await self.execute_query(query, params, database)

    async def delete_node(
        self,
        label: str,
        properties: dict,
        detach: bool = True,
        database: str | None = None,
    ) -> int:
        """
        Delete node(s) matching properties.

        Args:
            label: Node label
            properties: Properties to match
            detach: Also delete relationships (default True)
            database: Database name (optional)

        Returns:
            Number of nodes deleted

        Usage:
            deleted = await neo4j_helper.delete_node(
                "Person",
                {"name": "Alice"}
            )
        """
        props = " AND ".join(f"n.{k} = ${k}" for k in properties.keys())
        delete_clause = "DETACH DELETE" if detach else "DELETE"
        query = f"MATCH (n:{label}) WHERE {props} {delete_clause} n RETURN count(n) as deleted"

        result = await self.execute_write(query, properties, database)
        return result["data"][0].get("deleted", 0) if result["data"] else 0


# Global singleton instance
neo4j_helper = Neo4jHelper()
