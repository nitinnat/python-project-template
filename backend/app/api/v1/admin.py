"""
Admin endpoints for feature flags and system configuration.
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from app.helpers.postgres import postgres_helper
from app.schemas.feature_flag import FeatureFlagUpdate
from app.services.feature_flag_service import FeatureFlagService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/feature-flags")
async def get_feature_flags(
    category: str | None = Query(None, description="Filter by category")
) -> Dict[str, Any]:
    """
    Get all feature flags, optionally filtered by category.

    Args:
        category: Optional category filter

    Returns:
        List of feature flags with total count
    """
    async with postgres_helper.get_session() as session:
        service = FeatureFlagService(session)
        flags = await service.get_all_flags(category=category)

        # Convert to dict format
        flags_data = [
            {
                "id": flag.id,
                "key": flag.key,
                "name": flag.name,
                "description": flag.description,
                "category": flag.category,
                "enabled": flag.enabled,
                "metadata": flag.config,
                "created_at": flag.created_at.isoformat() if flag.created_at else None,
                "updated_at": flag.updated_at.isoformat() if flag.updated_at else None,
            }
            for flag in flags
        ]

        return {
            "flags": flags_data,
            "total": len(flags_data),
        }


@router.patch("/feature-flags/{key}")
async def update_feature_flag(
    key: str,
    update: FeatureFlagUpdate,
) -> Dict[str, Any]:
    """
    Update a feature flag.

    Args:
        key: Feature flag key
        update: Update data

    Returns:
        Updated feature flag

    Raises:
        HTTPException: If feature flag not found
    """
    async with postgres_helper.get_session() as session:
        service = FeatureFlagService(session)
        flag = await service.update_flag(key, update)

        if not flag:
            raise HTTPException(status_code=404, detail=f"Feature flag '{key}' not found")

        return {
            "id": flag.id,
            "key": flag.key,
            "name": flag.name,
            "description": flag.description,
            "category": flag.category,
            "enabled": flag.enabled,
            "metadata": flag.config,
            "created_at": flag.created_at.isoformat() if flag.created_at else None,
            "updated_at": flag.updated_at.isoformat() if flag.updated_at else None,
        }
