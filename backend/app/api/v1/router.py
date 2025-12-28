"""
API v1 router aggregator.

Combines all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import admin, documents, graph, health

api_router = APIRouter()

# Include health routes
api_router.include_router(health.router)

# Include admin routes
api_router.include_router(admin.router)

# Include document routes
api_router.include_router(documents.router)

# Include graph routes
api_router.include_router(graph.router)

# Additional routers can be added:
# - search_router (advanced vector search)
# - tasks_router (Celery task triggers)
# - llm_router (LLM endpoints)
