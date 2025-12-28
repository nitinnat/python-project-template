"""
Example Celery tasks for background processing.

These demonstrate common task patterns:
- Periodic cleanup
- Health checks
- Email sending
- Data processing
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict

from app.helpers.celery_app import celery_app
from app.core.logging import logger


@celery_app.task(name="app.tasks.example_tasks.cleanup_old_results")
def cleanup_old_results():
    """
    Periodic task to cleanup old Celery results.
    Runs daily at 2:00 AM (configured in celery_app.py).
    """
    try:
        from celery.result import AsyncResult

        # This is a simplified example
        # In production, you'd clean up your result backend
        logger.info("Running cleanup task")

        # Example: Delete results older than 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)

        # Add your cleanup logic here
        count = 0  # Track deleted items

        logger.info(f"Cleanup completed: {count} old results removed")
        return {"status": "success", "removed": count}

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="app.tasks.example_tasks.health_check")
def health_check():
    """
    Periodic health check task.
    Runs every 5 minutes (configured in celery_app.py).
    """
    try:
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "celery_worker": "healthy",
            "tasks_processed": celery_app.control.inspect().stats(),
        }

        logger.info("Health check completed")
        return status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@celery_app.task(
    name="app.tasks.example_tasks.send_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_email(self, to: str, subject: str, body: str):
    """
    Send email asynchronously.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body

    Returns:
        Dict with status and message
    """
    try:
        logger.info(f"Sending email to {to}: {subject}")

        # TODO: Implement actual email sending
        # Example with SMTP:
        # import smtplib
        # from email.message import EmailMessage
        # msg = EmailMessage()
        # msg.set_content(body)
        # msg['Subject'] = subject
        # msg['From'] = 'noreply@example.com'
        # msg['To'] = to
        # smtp = smtplib.SMTP('localhost')
        # smtp.send_message(msg)
        # smtp.quit()

        # For now, just log
        logger.info(f"Email sent successfully to {to}")

        return {
            "status": "success",
            "to": to,
            "subject": subject,
            "sent_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Email sending failed: {e}")

        # Retry with exponential backoff
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.example_tasks.process_data",
    bind=True,
    max_retries=3,
)
def process_data(self, data: Dict[str, Any]):
    """
    Process data in background.

    Args:
        data: Data to process

    Returns:
        Processed data
    """
    try:
        logger.info(f"Processing data: {data.get('id', 'unknown')}")

        # Simulate processing
        import time
        time.sleep(2)

        # Add processing logic here
        result = {
            "id": data.get("id"),
            "status": "processed",
            "processed_at": datetime.utcnow().isoformat(),
            "original_data": data,
        }

        logger.info(f"Data processed: {result['id']}")
        return result

    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(name="app.tasks.example_tasks.long_running_task")
def long_running_task(duration: int = 60):
    """
    Example long-running task.

    Args:
        duration: How long to run (seconds)
    """
    import time

    logger.info(f"Starting long-running task ({duration}s)")

    for i in range(duration):
        time.sleep(1)
        if i % 10 == 0:
            logger.info(f"Progress: {i}/{duration}")

    logger.info("Long-running task completed")
    return {"status": "completed", "duration": duration}


@celery_app.task(
    name="app.tasks.example_tasks.chain_example",
    bind=True,
)
def chain_example(self, value: int):
    """
    Example task for task chaining.

    Args:
        value: Input value
    """
    result = value * 2
    logger.info(f"Chain task: {value} -> {result}")
    return result
