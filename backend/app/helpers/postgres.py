from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class PostgreSQLHelper:
    """Singleton pattern to ensure single engine instance."""

    _instance = None
    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self):
        """Called during application startup."""
        if self._engine is not None:
            logger.warning("PostgreSQL already initialized")
            return

        try:
            self._engine = create_async_engine(
                settings.database_url,
                echo=settings.app_debug,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                future=True,
            )

            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            logger.info("PostgreSQL engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            raise

    async def close(self):
        """Called during application shutdown."""
        if self._engine is None:
            return

        try:
            await self._engine.dispose()
            logger.info("PostgreSQL connections closed")
        except Exception as e:
            logger.error(f"Error closing PostgreSQL connections: {e}")
        finally:
            self._engine = None
            self._session_factory = None

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_factory is None:
            raise RuntimeError(
                "Database not initialized. Call initialize() first."
            )

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    def get_engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError(
                "Database not initialized. Call initialize() first."
            )
        return self._engine

    async def execute_raw(self, query: str, params: dict | None = None):
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            return result

    async def vector_search(
        self,
        embedding: list[float],
        table: str,
        limit: int = 10,
        distance_threshold: float | None = None,
    ):
        """
        Requires PGVector extension and table with 'embedding' column of type vector.
        """
        if not settings.enable_pgvector:
            raise RuntimeError("PGVector is not enabled")

        if distance_threshold:
            query = f"""
                SELECT *, embedding <-> :embedding::vector as distance
                FROM {table}
                WHERE embedding <-> :embedding::vector < :threshold
                ORDER BY distance
                LIMIT :limit
            """
            params = {
                "embedding": str(embedding),
                "threshold": distance_threshold,
                "limit": limit,
            }
        else:
            query = f"""
                SELECT *, embedding <-> :embedding::vector as distance
                FROM {table}
                ORDER BY distance
                LIMIT :limit
            """
            params = {"embedding": str(embedding), "limit": limit}

        result = await self.execute_raw(query, params)
        return result.fetchall()


postgres_helper = PostgreSQLHelper()
