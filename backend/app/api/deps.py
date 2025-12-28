from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    from app.helpers.postgres import postgres_helper

    async with postgres_helper.get_session() as session:
        yield session


async def get_feature_flag_service(db: AsyncSession = Depends(get_db)):
    from app.services.feature_flag_service import FeatureFlagService

    return FeatureFlagService(db)


async def get_redis():
    from app.helpers.redis_helper import redis_helper

    return redis_helper.get_client()


async def get_mongodb():
    if not settings.enable_mongodb:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB is not enabled",
        )

    from app.helpers.mongodb import mongodb_helper

    return mongodb_helper.get_database()


async def get_neo4j():
    if not settings.enable_neo4j:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j is not enabled",
        )

    from app.helpers.neo4j_helper import neo4j_helper

    return neo4j_helper.get_driver()


async def get_neo4j_session():
    """Get Neo4j session for graph operations."""
    if not settings.enable_neo4j:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j is not enabled",
        )

    from app.helpers.neo4j_helper import neo4j_helper

    async with neo4j_helper.get_session() as session:
        yield session
