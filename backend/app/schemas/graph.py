"""
Graph schemas for Neo4j graph operations.

Pydantic models for nodes, relationships, and graph queries.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NodeBase(BaseModel):
    """Base node schema."""

    name: str = Field(..., min_length=1, max_length=255)
    node_type: str = Field(..., min_length=1, max_length=50)
    properties: Dict[str, Any] = Field(default_factory=dict)


class NodeCreate(NodeBase):
    """Schema for creating a node."""

    pass


class NodeUpdate(BaseModel):
    """Schema for updating a node."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    properties: Optional[Dict[str, Any]] = None


class NodeResponse(NodeBase):
    """Schema for node response."""

    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RelationshipBase(BaseModel):
    """Base relationship schema."""

    from_node_id: str
    to_node_id: str
    relationship_type: str = Field(..., min_length=1, max_length=50)
    properties: Dict[str, Any] = Field(default_factory=dict)


class RelationshipCreate(RelationshipBase):
    """Schema for creating a relationship."""

    pass


class RelationshipResponse(RelationshipBase):
    """Schema for relationship response."""

    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GraphQuery(BaseModel):
    """Schema for graph query."""

    query: str = Field(..., min_length=1)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class PathQuery(BaseModel):
    """Schema for path query."""

    from_node_id: str
    to_node_id: str
    max_depth: int = Field(default=5, ge=1, le=20)
    relationship_types: Optional[List[str]] = None


class PathResponse(BaseModel):
    """Schema for path response."""

    nodes: List[NodeResponse]
    relationships: List[RelationshipResponse]
    length: int


class NeighborsQuery(BaseModel):
    """Schema for neighbors query."""

    node_id: str
    relationship_types: Optional[List[str]] = None
    direction: str = Field(default="both")  # "incoming", "outgoing", "both"
    depth: int = Field(default=1, ge=1, le=3)


class NeighborsResponse(BaseModel):
    """Schema for neighbors response."""

    center_node: NodeResponse
    neighbors: List[NodeResponse]
    relationships: List[RelationshipResponse]
    total: int
