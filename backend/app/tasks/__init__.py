"""
Celery tasks package.

Tasks are organized by category:
- example_tasks: General purpose task examples
- llm_tasks: LLM-related background tasks
"""

from .example_tasks import (
    cleanup_old_results,
    health_check,
    send_email,
    process_data,
)

from .llm_tasks import (
    generate_embeddings,
    llm_completion_task,
    batch_generate_embeddings,
)

__all__ = [
    # Example tasks
    "cleanup_old_results",
    "health_check",
    "send_email",
    "process_data",
    # LLM tasks
    "generate_embeddings",
    "llm_completion_task",
    "batch_generate_embeddings",
]
