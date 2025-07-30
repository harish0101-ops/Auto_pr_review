# Start API
uvicorn app.main:app --reload

# Start worker
celery -A app.celery_worker worker --loglevel=info

# Start Redis separately
docker run -p 6379:6379 redis