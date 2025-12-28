"""
Decorators for feature flags and other cross-cutting concerns.

Provides decorators to protect endpoints and functions behind feature flags.
"""

from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, status


def require_feature(feature_key: str):
    """
    Decorator to protect endpoints behind runtime feature flags.

    Usage:
        @router.get("/documents")
        @require_feature("feature.vector_search")
        async def search_documents(
            query: str,
            flag_service: FeatureFlagService = Depends(get_feature_flag_service)
        ):
            ...

    Args:
        feature_key: The feature flag key to check

    Raises:
        HTTPException: 503 if feature is disabled
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract feature flag service from kwargs
            flag_service = kwargs.get("flag_service")

            if not flag_service:
                # Feature flag service not provided, allow the request
                # This allows gradual adoption of feature flags
                return await func(*args, **kwargs)

            # Check if feature is enabled
            if not await flag_service.is_enabled(feature_key):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Feature '{feature_key}' is currently disabled",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_build_time_feature(feature_name: str):
    """
    Decorator to check build-time feature flags.

    This checks settings to ensure a service is enabled before
    allowing the endpoint to execute.

    Usage:
        @router.get("/graph/search")
        @require_build_time_feature("neo4j")
        async def search_graph():
            ...

    Args:
        feature_name: Name of the build-time feature (e.g., "neo4j", "mongodb")

    Raises:
        HTTPException: 503 if feature is not enabled at build time
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            from app.config.settings import settings

            # Map feature names to settings attributes
            feature_mapping = {
                "neo4j": settings.enable_neo4j,
                "mongodb": settings.enable_mongodb,
                "rabbitmq": settings.enable_rabbitmq,
                "celery": settings.enable_celery_worker,
                "pgvector": settings.enable_pgvector,
            }

            is_enabled = feature_mapping.get(feature_name, False)

            if not is_enabled:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Service '{feature_name}' is not enabled. "
                    f"Enable it in features.env and restart services.",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
