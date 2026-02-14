from celery import Celery
from app.config import settings

celery_app = Celery(
    "taxflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    beat_schedule={
        "process-pending-withdrawals": {
            "task": "app.worker.tasks.process_pending_withdrawals",
            "schedule": 3600.0,  # every hour
        },
        "send-daily-digest": {
            "task": "app.worker.tasks.send_daily_digest",
            "schedule": 86400.0,  # daily
        },
        "reset-monthly-usage": {
            "task": "app.worker.tasks.reset_monthly_usage",
            "schedule": 86400.0,  # daily, but should run on first of month
        },
        "cleanup-expired-sessions": {
            "task": "app.worker.tasks.cleanup_expired_sessions",
            "schedule": 86400.0,
        },
    },
)
