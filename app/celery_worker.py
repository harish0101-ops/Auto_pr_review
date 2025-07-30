# app/celery_worker.py
from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "workautocode-reviewer",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.task_track_started = True
celery_app.conf.task_serializer = "json"
celery_app.autodiscover_tasks(["app.tasks"])

import app.tasks.review 
celery_app.set_default()