"""
Document schemas for MongoDB document storage.

Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document schema."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""

    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class DocumentInDB(DocumentBase):
    """Schema for document in database."""

    id: str = Field(..., alias="_id")
    user_id: int
    embedding: Optional[List[float]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    id: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DocumentList(BaseModel):
    """Schema for list of documents."""

    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class SearchQuery(BaseModel):
    """Schema for search query."""

    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    filters: Dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """Schema for search result."""

    document: DocumentResponse
    score: float
    relevance: str  # "high", "medium", "low"


class SearchResponse(BaseModel):
    """Schema for search response."""

    query: str
    results: List[SearchResult]
    total: int
