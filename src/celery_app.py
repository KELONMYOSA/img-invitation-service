from celery import Celery

from src.config import settings

celery_app = Celery(
    "img-invitation-service",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.tasks.invitation_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_time_limit=30,
    task_soft_time_limit=20,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=0,
    task_ignore_result=True,
)
