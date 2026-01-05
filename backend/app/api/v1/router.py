"""
API v1 router aggregator.

Combines all v1 endpoints.
"""

import importlib

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
    documents = importlib.import_module("app.api.v1.documents")
    api_router.include_router(documents.router)

# Include graph routes (only if Neo4j is enabled)
if settings.enable_neo4j:
    graph = importlib.import_module("app.api.v1.graph")
    api_router.include_router(graph.router)

# Include RAG routes (only if Ollama is enabled for embeddings)
if settings.enable_llm_ollama:
    rag = importlib.import_module("app.api.v1.rag")
    api_router.include_router(rag.router)

# Additional routers can be added:
# - search_router (advanced vector search)
# - tasks_router (Celery task triggers)
# - llm_router (LLM endpoints)
