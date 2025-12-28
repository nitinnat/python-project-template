"""
Document service for business logic.

Handles document operations with embeddings and search.
"""

from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.document_repository import DocumentRepository
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    SearchQuery,
    SearchResult,
)


class DocumentService:
    """Service for document operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.repository = DocumentRepository(db)

    async def create_document(
        self,
        document: DocumentCreate,
        user_id: int,
        generate_embedding: bool = False,
    ) -> DocumentResponse:
        """
        Create a new document.

        Args:
            document: Document data
            user_id: User ID
            generate_embedding: Whether to generate embeddings

        Returns:
            Created document
        """
        doc_dict = await self.repository.create(document, user_id)

        # Optionally generate embeddings in background
        if generate_embedding:
            from app.tasks.llm_tasks import generate_embeddings
            # Trigger async task
            generate_embeddings.delay(
                text=document.content,
                model="text-embedding-3-small"
            )

        return DocumentResponse(**doc_dict)

    async def get_document(self, document_id: str) -> Optional[DocumentResponse]:
        """Get document by ID."""
        doc = await self.repository.get(document_id)
        return DocumentResponse(**doc) if doc else None

    async def get_user_documents(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[DocumentResponse]:
        """Get documents for a user."""
        docs = await self.repository.get_by_user(user_id, skip, limit)
        return [DocumentResponse(**doc) for doc in docs]

    async def update_document(
        self,
        document_id: str,
        document: DocumentUpdate,
    ) -> Optional[DocumentResponse]:
        """Update document."""
        doc = await self.repository.update(document_id, document)
        return DocumentResponse(**doc) if doc else None

    async def delete_document(self, document_id: str) -> bool:
        """Delete document."""
        return await self.repository.delete(document_id)

    async def search_documents(
        self,
        query: SearchQuery,
        user_id: Optional[int] = None,
    ) -> List[SearchResult]:
        """
        Search documents.

        Args:
            query: Search query
            user_id: Optional user filter

        Returns:
            List of search results with scores
        """
        filters = query.filters.copy() if query.filters else {}
        if user_id:
            filters["user_id"] = user_id

        docs = await self.repository.search(
            query.query,
            filters=filters,
            limit=query.limit,
        )

        # Convert to search results with dummy scores
        # In production, use actual relevance scoring
        results = []
        for i, doc in enumerate(docs):
            score = 1.0 - (i * 0.1)  # Decreasing score
            relevance = "high" if score > 0.7 else "medium" if score > 0.4 else "low"

            results.append(
                SearchResult(
                    document=DocumentResponse(**doc),
                    score=score,
                    relevance=relevance,
                )
            )

        return results

    async def add_embedding(
        self,
        document_id: str,
        embedding: List[float],
    ) -> bool:
        """Add embedding to document."""
        return await self.repository.add_embedding(document_id, embedding)
