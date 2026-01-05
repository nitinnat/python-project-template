"""
RAG (Retrieval-Augmented Generation) services.

This package contains all services for the RAG system:
- EmbeddingService: Generate embeddings using Ollama
- IngestionService: Process and ingest documents
- RagChatAgent: LangGraph-based chat agent
- RagService: Facade service orchestrating all operations
"""

from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.rag_service import RagService

__all__ = [
    "EmbeddingService",
    "RagService",
]
