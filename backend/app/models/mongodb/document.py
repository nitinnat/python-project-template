"""
MongoDB document models using Pydantic.

Example document model for storing unstructured data.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Example document model for MongoDB.

    Demonstrates storing unstructured/semi-structured data.
    """

    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    tags: list[str] = Field(default_factory=list, description="Document tags")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Example Document",
                "content": "This is an example document stored in MongoDB",
                "tags": ["example", "mongodb"],
                "metadata": {"author": "system", "version": 1},
            }
        }
