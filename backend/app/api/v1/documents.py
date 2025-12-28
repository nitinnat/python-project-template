"""
Documents API endpoints.

Handles document CRUD and search operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_mongodb
from app.schemas.document import (
    DocumentCreate,
    DocumentList,
    DocumentResponse,
    DocumentUpdate,
    SearchQuery,
    SearchResponse,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    generate_embedding: bool = Query(default=False),
    db = Depends(get_mongodb),
):
    """
    Create a new document.

    Args:
        document: Document data
        generate_embedding: Whether to generate embeddings (async)
        db: MongoDB database

    Returns:
        Created document
    """
    service = DocumentService(db)
    return await service.create_document(
        document,
        user_id=None,  # No user authentication
        generate_embedding=generate_embedding,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """
    Get document by ID.

    Args:
        document_id: Document ID
        db: MongoDB database

    Returns:
        Document data
    """
    service = DocumentService(db)
    document = await service.get_document(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.get("/", response_model=DocumentList)
async def list_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """
    List all documents.

    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        db: MongoDB database

    Returns:
        List of documents
    """
    service = DocumentService(db)

    documents = await service.repository.find_all(skip=skip, limit=limit)
    total = await service.repository.count_all()

    return DocumentList(
        documents=documents,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document: DocumentUpdate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """
    Update document.

    Args:
        document_id: Document ID
        document: Update data
        db: MongoDB database

    Returns:
        Updated document
    """
    service = DocumentService(db)

    # Check if exists
    existing = await service.get_document(document_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    updated = await service.update_document(document_id, document)
    return updated


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """
    Delete document.

    Args:
        document_id: Document ID
        db: MongoDB database
    """
    service = DocumentService(db)

    # Check if exists
    existing = await service.get_document(document_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    deleted = await service.delete_document(document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    query: SearchQuery,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """
    Search documents.

    Args:
        query: Search query
        db: MongoDB database

    Returns:
        Search results
    """
    service = DocumentService(db)

    results = await service.search_documents(query, user_id=None)

    return SearchResponse(
        query=query.query,
        results=results,
        total=len(results),
    )
