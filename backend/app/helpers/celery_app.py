"""
Celery application configuration.

Features:
- RabbitMQ as message broker
- Redis as result backend
- Task routing by queue
- Automatic retries with exponential backoff
- Task monitoring and logging
"""

from celery import Celery
from celery.schedules import crontab

from app.config.settings import settings

# Create Celery app
celery_app = Celery(
    "tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit

    # Task retry settings
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,

    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,

    # Task routing
    task_routes={
        "app.tasks.example_tasks.*": {"queue": "default"},
        "app.tasks.llm_tasks.*": {"queue": "llm"},
    },

    # Result backend settings
    result_expires=86400,  # 24 hours
    result_persistent=True,

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Periodic tasks (Celery Beat schedule)
celery_app.conf.beat_schedule = {
    "cleanup-old-results": {
        "task": "app.tasks.example_tasks.cleanup_old_results",
        "schedule": crontab(hour=2, minute=0),  # Run at 2:00 AM daily
    },
    "health-check": {
        "task": "app.tasks.example_tasks.health_check",
        "schedule": 300.0,  # Every 5 minutes
    },
}

# Auto-discover tasks from installed apps
celery_app.autodiscover_tasks(["app.tasks"])

__all__ = ["celery_app"]
