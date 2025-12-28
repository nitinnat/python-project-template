"""
Feature flag service for managing runtime feature toggles.

Provides caching and database operations for feature flags.
"""

import asyncio
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.postgres.feature_flag import FeatureFlag
from app.schemas.feature_flag import FeatureFlagCreate, FeatureFlagUpdate

logger = get_logger(__name__)


class FeatureFlagService:
    """Service for managing runtime feature flags."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._cache: dict[str, bool] = {}
        self._cache_ttl = 60  # seconds

    async def is_enabled(self, key: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            key: Feature flag key

        Returns:
            True if enabled, False otherwise
        """
        # Check cache first
        if key in self._cache:
            logger.debug(f"Feature flag cache hit: {key}")
            return self._cache[key]

        # Query database
        result = await self.session.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        flag = result.scalar_one_or_none()

        enabled = flag.enabled if flag else False
        self._cache[key] = enabled

        # Auto-expire cache after TTL
        asyncio.create_task(self._expire_cache(key))

        logger.debug(f"Feature flag cache miss: {key} = {enabled}")
        return enabled

    async def _expire_cache(self, key: str):
        """
        Expire cache entry after TTL.

        Args:
            key: Feature flag key
        """
        await asyncio.sleep(self._cache_ttl)
        self._cache.pop(key, None)
        logger.debug(f"Feature flag cache expired: {key}")

    def invalidate_cache(self, key: str | None = None):
        """
        Invalidate cache for specific key or all keys.

        Args:
            key: Feature flag key (None to clear all)
        """
        if key:
            self._cache.pop(key, None)
            logger.debug(f"Feature flag cache invalidated: {key}")
        else:
            self._cache.clear()
            logger.debug("All feature flag cache cleared")

    async def get_flag(self, key: str) -> FeatureFlag | None:
        """
        Get feature flag by key.

        Args:
            key: Feature flag key

        Returns:
            FeatureFlag or None if not found
        """
        result = await self.session.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        return result.scalar_one_or_none()

    async def get_flag_by_id(self, flag_id: int) -> FeatureFlag | None:
        """
        Get feature flag by ID.

        Args:
            flag_id: Feature flag ID

        Returns:
            FeatureFlag or None if not found
        """
        result = await self.session.execute(
            select(FeatureFlag).where(FeatureFlag.id == flag_id)
        )
        return result.scalar_one_or_none()

    async def get_all_flags(
        self, category: str | None = None
    ) -> list[FeatureFlag]:
        """
        Get all feature flags, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of feature flags
        """
        query = select(FeatureFlag)

        if category:
            query = query.where(FeatureFlag.category == category)

        query = query.order_by(FeatureFlag.category, FeatureFlag.key)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_flag(self, data: FeatureFlagCreate) -> FeatureFlag:
        """
        Create a new feature flag.

        Args:
            data: Feature flag creation data

        Returns:
            Created feature flag
        """
        flag = FeatureFlag(
            key=data.key,
            name=data.name,
            description=data.description,
            enabled=data.enabled,
            category=data.category,
            metadata=data.metadata,
        )

        self.session.add(flag)
        await self.session.commit()
        await self.session.refresh(flag)

        logger.info(f"Created feature flag: {flag.key}")
        return flag

    async def update_flag(
        self, key: str, data: FeatureFlagUpdate
    ) -> FeatureFlag | None:
        """
        Update an existing feature flag.

        Args:
            key: Feature flag key
            data: Update data

        Returns:
            Updated feature flag or None if not found
        """
        result = await self.session.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        flag = result.scalar_one_or_none()

        if not flag:
            return None

        # Update fields if provided
        if data.enabled is not None:
            flag.enabled = data.enabled
        if data.name is not None:
            flag.name = data.name
        if data.description is not None:
            flag.description = data.description
        if data.category is not None:
            flag.category = data.category
        if data.metadata is not None:
            flag.metadata = data.metadata

        await self.session.commit()
        await self.session.refresh(flag)

        # Invalidate cache
        self.invalidate_cache(key)

        logger.info(f"Updated feature flag: {key}")
        return flag

    async def set_flag(
        self,
        key: str,
        enabled: bool,
        metadata: dict[str, Any] | None = None,
    ) -> FeatureFlag:
        """
        Set or update a feature flag (creates if doesn't exist).

        Args:
            key: Feature flag key
            enabled: Whether feature is enabled
            metadata: Optional metadata

        Returns:
            Created or updated feature flag
        """
        result = await self.session.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        flag = result.scalar_one_or_none()

        if flag:
            flag.enabled = enabled
            if metadata:
                flag.metadata = metadata
        else:
            flag = FeatureFlag(
                key=key,
                name=key.replace(".", " ").replace("_", " ").title(),
                enabled=enabled,
                metadata=metadata,
            )
            self.session.add(flag)

        await self.session.commit()
        await self.session.refresh(flag)

        # Invalidate cache
        self.invalidate_cache(key)

        logger.info(f"Set feature flag: {key} = {enabled}")
        return flag

    async def delete_flag(self, key: str) -> bool:
        """
        Delete a feature flag.

        Args:
            key: Feature flag key

        Returns:
            True if deleted, False if not found
        """
        result = await self.session.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        flag = result.scalar_one_or_none()

        if not flag:
            return False

        await self.session.delete(flag)
        await self.session.commit()

        # Invalidate cache
        self.invalidate_cache(key)

        logger.info(f"Deleted feature flag: {key}")
        return True

    async def bulk_update(self, keys: list[str], enabled: bool) -> int:
        """
        Bulk update multiple feature flags.

        Args:
            keys: List of feature flag keys
            enabled: Enable or disable

        Returns:
            Number of flags updated
        """
        result = await self.session.execute(
            select(FeatureFlag).where(FeatureFlag.key.in_(keys))
        )
        flags = result.scalars().all()

        count = 0
        for flag in flags:
            flag.enabled = enabled
            self.invalidate_cache(flag.key)
            count += 1

        await self.session.commit()

        logger.info(f"Bulk updated {count} feature flags to enabled={enabled}")
        return count

    async def get_flags_by_category(self) -> dict[str, list[FeatureFlag]]:
        """
        Get all feature flags grouped by category.

        Returns:
            Dictionary with category as key and list of flags as value
        """
        result = await self.session.execute(
            select(FeatureFlag).order_by(FeatureFlag.category, FeatureFlag.key)
        )
        flags = result.scalars().all()

        grouped: dict[str, list[FeatureFlag]] = {}
        for flag in flags:
            if flag.category not in grouped:
                grouped[flag.category] = []
            grouped[flag.category].append(flag)

        return grouped
