"""
API v1 router aggregator.

Combines all v1 endpoints.
"""

import importlib
import logging

from fastapi import APIRouter

from app.api.v1 import admin, health
from app.config.settings import settings

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Include health routes
api_router.include_router(health.router)

# Include admin routes
api_router.include_router(admin.router)

# Include document routes (only if MongoDB is enabled)
if settings.enable_mongodb:
    try:
        documents = importlib.import_module("app.api.v1.documents")
        api_router.include_router(documents.router)
        logger.info("MongoDB routes registered")
    except ImportError as e:
        logger.error(
            "MongoDB is enabled in .env but dependencies are not installed. "
            "Rebuild container with: docker compose build backend"
        )
        logger.debug(f"Import error details: {e}")

# Include graph routes (only if Neo4j is enabled)
if settings.enable_neo4j:
    try:
        graph = importlib.import_module("app.api.v1.graph")
        api_router.include_router(graph.router)
        logger.info("Neo4j routes registered")
    except ImportError as e:
        logger.error(
            "Neo4j is enabled in .env but dependencies are not installed. "
            "Rebuild container with: docker compose build backend"
        )
        logger.debug(f"Import error details: {e}")

# Additional routers can be added:
# - search_router (advanced vector search)
# - tasks_router (Celery task triggers)
# - llm_router (LLM endpoints)
