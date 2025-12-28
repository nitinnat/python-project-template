"""
Document repository for MongoDB operations.

Handles CRUD operations for documents in MongoDB.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentRepository:
    """Repository for document operations in MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.get_collection("documents")

    async def create(self, document: DocumentCreate, user_id: int) -> Dict[str, Any]:
        """
        Create a new document.

        Args:
            document: Document data
            user_id: User ID creating the document

        Returns:
            Created document with ID
        """
        doc_dict = document.model_dump()
        doc_dict.update({
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": None,
        })

        result = await self.collection.insert_one(doc_dict)
        doc_dict["_id"] = str(result.inserted_id)

        return doc_dict

    async def get(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document data or None
        """
        try:
            doc = await self.collection.find_one({"_id": ObjectId(document_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception:
            return None

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get documents by user.

        Args:
            user_id: User ID
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of documents
        """
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        for doc in docs:
            doc["_id"] = str(doc["_id"])

        return docs

    async def update(
        self,
        document_id: str,
        document: DocumentUpdate,
    ) -> Optional[Dict[str, Any]]:
        """
        Update document.

        Args:
            document_id: Document ID
            document: Update data

        Returns:
            Updated document or None
        """
        try:
            update_data = {
                k: v for k, v in document.model_dump().items() if v is not None
            }
            update_data["updated_at"] = datetime.utcnow()

            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(document_id)},
                {"$set": update_data},
                return_document=True,
            )

            if result:
                result["_id"] = str(result["_id"])

            return result
        except Exception:
            return None

    async def delete(self, document_id: str) -> bool:
        """
        Delete document.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search documents by text.

        Args:
            query: Search query
            filters: Additional filters
            limit: Maximum number of results

        Returns:
            List of matching documents
        """
        search_filter = {"$text": {"$search": query}}

        if filters:
            search_filter.update(filters)

        cursor = self.collection.find(search_filter).limit(limit)
        docs = await cursor.to_list(length=limit)

        for doc in docs:
            doc["_id"] = str(doc["_id"])

        return docs

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get all documents.

        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of documents
        """
        cursor = self.collection.find({}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        for doc in docs:
            doc["_id"] = str(doc["_id"])

        return docs

    async def count_all(self) -> int:
        """
        Count all documents.

        Returns:
            Number of documents
        """
        return await self.collection.count_documents({})

    async def count_by_user(self, user_id: int) -> int:
        """
        Count documents by user.

        Args:
            user_id: User ID

        Returns:
            Number of documents
        """
        return await self.collection.count_documents({"user_id": user_id})

    async def add_embedding(
        self,
        document_id: str,
        embedding: List[float],
    ) -> bool:
        """
        Add embedding to document.

        Args:
            document_id: Document ID
            embedding: Embedding vector

        Returns:
            True if successful
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": {"embedding": embedding}},
            )
            return result.modified_count > 0
        except Exception:
            return False
