"""
LLM-related Celery tasks.

Background tasks for LLM operations:
- Embedding generation
- Batch processing
- LLM completions
- Document processing
"""

import asyncio
from typing import Any, Dict, List, Optional

from app.helpers.celery_app import celery_app
from app.core.logging import logger


def run_async(coro):
    """Helper to run async functions in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="app.tasks.llm_tasks.generate_embeddings",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_embeddings(self, text: str, model: str = "text-embedding-3-small"):
    """
    Generate embeddings for text using OpenAI.

    Args:
        text: Text to generate embeddings for
        model: Embedding model to use

    Returns:
        Dict with embedding vector and metadata
    """
    try:
        from app.helpers.llm.openai_client import openai_client

        logger.info(f"Generating embeddings for text (length: {len(text)})")

        # Run async function in sync context
        embedding = run_async(openai_client.create_embedding(text, model=model))

        logger.info(f"Embeddings generated: {len(embedding)} dimensions")

        return {
            "embedding": embedding,
            "model": model,
            "dimensions": len(embedding),
            "text_length": len(text),
        }

    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.llm_tasks.batch_generate_embeddings",
    bind=True,
    max_retries=3,
)
def batch_generate_embeddings(
    self,
    texts: List[str],
    model: str = "text-embedding-3-small",
):
    """
    Generate embeddings for multiple texts.

    Args:
        texts: List of texts to generate embeddings for
        model: Embedding model to use

    Returns:
        List of embedding vectors
    """
    try:
        from app.helpers.llm.openai_client import openai_client

        logger.info(f"Generating embeddings for {len(texts)} texts")

        # Run async function in sync context
        embeddings = run_async(
            openai_client.create_embeddings(texts, model=model)
        )

        logger.info(f"Batch embeddings generated: {len(embeddings)}")

        return {
            "embeddings": embeddings,
            "count": len(embeddings),
            "model": model,
        }

    except Exception as e:
        logger.error(f"Batch embedding generation failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.llm_tasks.llm_completion_task",
    bind=True,
    max_retries=3,
)
def llm_completion_task(
    self,
    messages: List[Dict[str, str]],
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
):
    """
    Generate LLM completion in background.

    Args:
        messages: Conversation messages
        model: LLM model to use
        temperature: Sampling temperature

    Returns:
        Completion response
    """
    try:
        from app.helpers.llm.litellm_client import litellm_client

        logger.info(f"Generating LLM completion with {model}")

        # Run async function in sync context
        response = run_async(
            litellm_client.complete(
                messages=messages,
                model=model,
                temperature=temperature,
            )
        )

        logger.info(f"LLM completion generated: {len(response['content'])} chars")

        return response

    except Exception as e:
        logger.error(f"LLM completion failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.llm_tasks.process_document_with_llm",
    bind=True,
)
def process_document_with_llm(
    self,
    document_id: int,
    operation: str = "summarize",
):
    """
    Process document using LLM.

    Args:
        document_id: Document ID to process
        operation: Operation to perform (summarize, extract, classify, etc.)

    Returns:
        Processing result
    """
    try:
        logger.info(f"Processing document {document_id} with LLM: {operation}")

        # TODO: Fetch document from database
        # from app.repositories.document_repository import DocumentRepository
        # async with get_db() as session:
        #     repo = DocumentRepository(session)
        #     document = await repo.get(document_id)

        # Placeholder for document content
        document_content = f"Document {document_id} content..."

        # Perform operation based on type
        if operation == "summarize":
            prompt = f"Summarize the following document:\n\n{document_content}"
        elif operation == "extract":
            prompt = f"Extract key information from:\n\n{document_content}"
        elif operation == "classify":
            prompt = f"Classify the following document:\n\n{document_content}"
        else:
            prompt = document_content

        from app.helpers.llm.litellm_client import litellm_client

        response = run_async(
            litellm_client.complete(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-3.5-turbo",
            )
        )

        logger.info(f"Document {document_id} processed successfully")

        return {
            "document_id": document_id,
            "operation": operation,
            "result": response["content"],
            "tokens_used": response["usage"]["total_tokens"],
            "cost": response["cost"],
        }

    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.llm_tasks.rag_query_task",
    bind=True,
)
def rag_query_task(
    self,
    query: str,
    collection_name: str = "documents",
    model: str = "gpt-3.5-turbo",
):
    """
    Perform RAG query in background.

    Args:
        query: User query
        collection_name: Vector collection to search
        model: LLM model to use

    Returns:
        RAG response with sources
    """
    try:
        from app.helpers.llm.langchain_client import langchain_client

        logger.info(f"Performing RAG query: {query[:50]}...")

        response = run_async(
            langchain_client.rag_query(
                query=query,
                collection_name=collection_name,
                model=model,
            )
        )

        logger.info(f"RAG query completed: {len(response['sources'])} sources")

        return response

    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise self.retry(exc=e)
