"""
API v1 router aggregator.

Combines all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import admin, health
from app.config.settings import settings

api_router = APIRouter()

# Include health routes
api_router.include_router(health.router)

# Include admin routes
api_router.include_router(admin.router)

# Include document routes (only if MongoDB is enabled)
if settings.enable_mongodb:
    from app.api.v1 import documents
    api_router.include_router(documents.router)

# Include graph routes (only if Neo4j is enabled)
if settings.enable_neo4j:
    from app.api.v1 import graph
    api_router.include_router(graph.router)

# Additional routers can be added:
# - search_router (advanced vector search)
# - tasks_router (Celery task triggers)
# - llm_router (LLM endpoints)
