"""
Pydantic schemas for feature flags.

Request/response models for feature flag API endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FeatureFlagBase(BaseModel):
    """Base feature flag schema with common fields."""

    key: str = Field(..., min_length=1, max_length=100, description="Unique feature key")
    name: str = Field(..., min_length=1, max_length=255, description="Feature name")
    description: str | None = Field(None, max_length=500, description="Feature description")
    category: str = Field(
        default="feature",
        max_length=50,
        description="Feature category (database, llm, feature, integration)",
    )
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class FeatureFlagCreate(FeatureFlagBase):
    """Schema for creating a new feature flag."""

    enabled: bool = Field(default=False, description="Whether feature is enabled")


class FeatureFlagUpdate(BaseModel):
    """Schema for updating a feature flag."""

    enabled: bool | None = Field(None, description="Whether feature is enabled")
    name: str | None = Field(None, min_length=1, max_length=255, description="Feature name")
    description: str | None = Field(None, max_length=500, description="Feature description")
    category: str | None = Field(None, max_length=50, description="Feature category")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class FeatureFlagResponse(FeatureFlagBase):
    """Schema for feature flag response."""

    id: int
    enabled: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class FeatureFlagList(BaseModel):
    """Schema for list of feature flags."""

    flags: list[FeatureFlagResponse]
    total: int = Field(..., description="Total number of flags")


class FeatureFlagStatusResponse(BaseModel):
    """Schema for checking if a feature is enabled."""

    key: str
    enabled: bool
    message: str | None = None


class FeatureFlagBulkUpdate(BaseModel):
    """Schema for bulk updating feature flags."""

    keys: list[str] = Field(..., min_length=1, description="List of feature flag keys")
    enabled: bool = Field(..., description="Enable or disable all specified flags")
