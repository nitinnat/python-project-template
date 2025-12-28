"""
Redis helper for caching and session storage.

Provides:
- Async Redis client
- Key-value operations
- Pub/sub support
- TTL management
- Cache decorators
"""

import json
from functools import wraps
from typing import Any, Callable

from redis import asyncio as aioredis

from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisHelper:
    """
    Redis cache helper using async redis client.

    Implements singleton pattern for single client instance.
    """

    _instance = None
    _client: aioredis.Redis | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self):
        """
        Initialize Redis client.

        Called during application startup.
        """
        if self._client is not None:
            logger.warning("Redis already initialized")
            return

        try:
            self._client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10,
            )

            # Test connection
            await self._client.ping()

            logger.info("Redis client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def close(self):
        """
        Close Redis connection.

        Called during application shutdown.
        """
        if self._client is None:
            return

        try:
            await self._client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
        finally:
            self._client = None

    def get_client(self) -> aioredis.Redis:
        """
        Get Redis client instance.

        Returns:
            Redis client

        Raises:
            RuntimeError: If Redis not initialized
        """
        if self._client is None:
            raise RuntimeError("Redis not initialized. Call initialize() first.")
        return self._client

    async def get(self, key: str) -> Any | None:
        """
        Get value by key.

        Args:
            key: Cache key

        Returns:
            Value or None if not found
        """
        client = self.get_client()
        value = await client.get(key)

        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """
        Set key-value pair with optional TTL.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized if not string)
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful
        """
        client = self.get_client()

        # Serialize non-string values
        if not isinstance(value, str):
            value = json.dumps(value)

        if ttl:
            return await client.setex(key, ttl, value)
        else:
            return await client.set(key, value)

    async def delete(self, key: str) -> int:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            Number of keys deleted
        """
        client = self.get_client()
        return await client.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Check if key exists.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        client = self.get_client()
        return await client.exists(key) > 0

    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set TTL on existing key.

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        client = self.get_client()
        return await client.expire(key, ttl)

    async def incr(self, key: str, amount: int = 1) -> int:
        """
        Increment key value.

        Args:
            key: Cache key
            amount: Amount to increment (default 1)

        Returns:
            New value after increment
        """
        client = self.get_client()
        return await client.incrby(key, amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """
        Decrement key value.

        Args:
            key: Cache key
            amount: Amount to decrement (default 1)

        Returns:
            New value after decrement
        """
        client = self.get_client()
        return await client.decrby(key, amount)

    async def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        client = self.get_client()
        keys = await client.keys(pattern)
        if keys:
            return await client.delete(*keys)
        return 0

    def cache(self, ttl: int = 300, key_prefix: str = ""):
        """
        Decorator for caching function results.

        Args:
            ttl: Cache TTL in seconds (default 300)
            key_prefix: Optional key prefix

        Usage:
            @redis_helper.cache(ttl=600, key_prefix="user")
            async def get_user(user_id: int):
                return await fetch_user(user_id)
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                key_parts = [key_prefix, func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(filter(None, key_parts))

                # Try to get from cache
                cached = await self.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached

                # Call function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)
                logger.debug(f"Cache miss: {cache_key}")

                return result

            return wrapper

        return decorator


# Global singleton instance
redis_helper = RedisHelper()
