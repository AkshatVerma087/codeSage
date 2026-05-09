"""Celery application factory with Redis broker configuration."""

from celery import Celery
from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# Initialize Celery app
celery_app = Celery("codesage-ai-service")

# Load configuration
settings = get_settings()

# Configure Celery with Redis broker and result backend
celery_app.conf.update(
    broker_url=settings.redis_url,
    result_backend=settings.redis_url,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task result expiration: 24 hours
    result_expires=86400,
    # Task timeout: 1 hour (indexing can be slow)
    task_soft_time_limit=3600,
    task_time_limit=3700,
    # Worker pool size
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    # Task acknowledgment: task_acks_late allows retry on worker crash
    task_acks_late=True,
)

# Auto-discover tasks from app/tasks/ module
celery_app.autodiscover_tasks(["app.tasks"])


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    logger.info(f"Debug task request: {self.request!r}")
    return "Celery is working!"


__all__ = ["celery_app"]
