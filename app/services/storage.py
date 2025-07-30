import redis
import json
import os

r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

def save_result(task_id: str, data: dict):
    r.set(task_id, json.dumps(data), ex=86400)  # 1 day TTL

def get_result(task_id: str):
    value = r.get(task_id)
    if value:
        return json.loads(value)
    return None
