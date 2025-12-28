"""
MongoDB helper using Motor async driver.

Provides:
- Connection pool management
- Database and collection getters
- CRUD operations wrapper
- Aggregation pipeline helpers
- Full-text search support
- GridFS for file storage
"""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MongoDBHelper:
    """
    MongoDB helper using Motor async driver.

    Implements singleton pattern for single client instance.
    """

    _instance = None
    _client: AsyncIOMotorClient | None = None
    _database: AsyncIOMotorDatabase | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self):
        """
        Initialize MongoDB client and database.

        Called during application startup.
        """
        if self._client is not None:
            logger.warning("MongoDB already initialized")
            return

        try:
            # Create async client
            self._client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=10,
            )

            # Get database
            self._database = self._client[settings.mongodb_db]

            # Test connection
            await self._client.admin.command("ping")

            logger.info("MongoDB client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {e}")
            raise

    async def close(self):
        """
        Close MongoDB connection.

        Called during application shutdown.
        """
        if self._client is None:
            return

        try:
            self._client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
        finally:
            self._client = None
            self._database = None

    def get_client(self) -> AsyncIOMotorClient:
        """
        Get MongoDB client.

        Returns:
            AsyncIOMotorClient instance

        Raises:
            RuntimeError: If MongoDB not initialized
        """
        if self._client is None:
            raise RuntimeError("MongoDB not initialized. Call initialize() first.")
        return self._client

    def get_database(self) -> AsyncIOMotorDatabase:
        """
        Get MongoDB database.

        Returns:
            AsyncIOMotorDatabase instance

        Raises:
            RuntimeError: If MongoDB not initialized
        """
        if self._database is None:
            raise RuntimeError("MongoDB not initialized. Call initialize() first.")
        return self._database

    def get_collection(self, collection_name: str):
        """
        Get collection from database.

        Args:
            collection_name: Name of the collection

        Returns:
            Motor collection instance
        """
        database = self.get_database()
        return database[collection_name]

    async def insert_one(self, collection: str, document: dict) -> str:
        """
        Insert a single document.

        Args:
            collection: Collection name
            document: Document to insert

        Returns:
            Inserted document ID as string
        """
        coll = self.get_collection(collection)
        result = await coll.insert_one(document)
        return str(result.inserted_id)

    async def insert_many(self, collection: str, documents: list[dict]) -> list[str]:
        """
        Insert multiple documents.

        Args:
            collection: Collection name
            documents: List of documents to insert

        Returns:
            List of inserted document IDs
        """
        coll = self.get_collection(collection)
        result = await coll.insert_many(documents)
        return [str(id_) for id_ in result.inserted_ids]

    async def find_one(
        self, collection: str, filter_: dict, projection: dict | None = None
    ) -> dict | None:
        """
        Find a single document.

        Args:
            collection: Collection name
            filter_: Query filter
            projection: Fields to include/exclude (optional)

        Returns:
            Document or None if not found
        """
        coll = self.get_collection(collection)
        return await coll.find_one(filter_, projection)

    async def find_many(
        self,
        collection: str,
        filter_: dict | None = None,
        projection: dict | None = None,
        limit: int | None = None,
        skip: int = 0,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[dict]:
        """
        Find multiple documents.

        Args:
            collection: Collection name
            filter_: Query filter (optional, returns all if None)
            projection: Fields to include/exclude (optional)
            limit: Maximum number of documents (optional)
            skip: Number of documents to skip (default 0)
            sort: Sort order as list of (field, direction) tuples (optional)

        Returns:
            List of documents
        """
        coll = self.get_collection(collection)
        cursor = coll.find(filter_ or {}, projection)

        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        if sort:
            cursor = cursor.sort(sort)

        return await cursor.to_list(length=limit)

    async def update_one(
        self, collection: str, filter_: dict, update: dict, upsert: bool = False
    ) -> int:
        """
        Update a single document.

        Args:
            collection: Collection name
            filter_: Query filter
            update: Update operations (must use update operators like $set)
            upsert: Create document if not found (default False)

        Returns:
            Number of documents modified
        """
        coll = self.get_collection(collection)
        result = await coll.update_one(filter_, update, upsert=upsert)
        return result.modified_count

    async def update_many(
        self, collection: str, filter_: dict, update: dict
    ) -> int:
        """
        Update multiple documents.

        Args:
            collection: Collection name
            filter_: Query filter
            update: Update operations (must use update operators like $set)

        Returns:
            Number of documents modified
        """
        coll = self.get_collection(collection)
        result = await coll.update_many(filter_, update)
        return result.modified_count

    async def delete_one(self, collection: str, filter_: dict) -> int:
        """
        Delete a single document.

        Args:
            collection: Collection name
            filter_: Query filter

        Returns:
            Number of documents deleted
        """
        coll = self.get_collection(collection)
        result = await coll.delete_one(filter_)
        return result.deleted_count

    async def delete_many(self, collection: str, filter_: dict) -> int:
        """
        Delete multiple documents.

        Args:
            collection: Collection name
            filter_: Query filter

        Returns:
            Number of documents deleted
        """
        coll = self.get_collection(collection)
        result = await coll.delete_many(filter_)
        return result.deleted_count

    async def aggregate(
        self, collection: str, pipeline: list[dict]
    ) -> list[dict]:
        """
        Execute aggregation pipeline.

        Args:
            collection: Collection name
            pipeline: Aggregation pipeline stages

        Returns:
            List of aggregation results
        """
        coll = self.get_collection(collection)
        cursor = coll.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def count_documents(
        self, collection: str, filter_: dict | None = None
    ) -> int:
        """
        Count documents matching filter.

        Args:
            collection: Collection name
            filter_: Query filter (optional, counts all if None)

        Returns:
            Number of matching documents
        """
        coll = self.get_collection(collection)
        return await coll.count_documents(filter_ or {})


# Global singleton instance
mongodb_helper = MongoDBHelper()
