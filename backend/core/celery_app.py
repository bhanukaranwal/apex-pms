from celery import Celery
from celery.schedules import crontab
from backend.core.config import settings

celery_app = Celery(
    "apex_pms",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

celery_app.conf.beat_schedule = {
    "ingest-daily-prices": {
        "task": "backend.tasks.ingest_daily_prices",
        "schedule": crontab(hour=18, minute=0),
    },
    "calculate-portfolio-metrics": {
        "task": "backend.tasks.calculate_portfolio_metrics",
        "schedule": crontab(hour=19, minute=0),
    },
    "run-compliance-checks": {
        "task": "backend.tasks.run_compliance_checks",
        "schedule": crontab(hour=8, minute=0),
    },
    "retrain-ml-models": {
        "task": "backend.tasks.retrain_ml_models",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),
    },
}
