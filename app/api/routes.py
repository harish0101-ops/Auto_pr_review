from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel
from celery.result import AsyncResult
from app.services import storage
import hmac
import os

import hashlib

router = APIRouter()


def verify_github_signature(secret: str, payload: bytes, signature: str):
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    expected = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected, signature)

class AnalyzePRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: str = None

@router.post("/analyze-pr")
def analyze_pr(request: AnalyzePRRequest):
    from app.tasks.review import analyze_pr_task
    task = analyze_pr_task.delay(request.repo_url, request.pr_number, request.github_token)
    return {"task_id": task.id}

@router.get("/status/{task_id}")
def get_status(task_id: str):
    result = storage.get_result(task_id)
    if result is None:
        return {"task_id": task_id, "status": "PENDING"}
    elif isinstance(result, dict) and "error" in result:
        return {"task_id": task_id, "status": "FAILED", "error": result["error"]}
    else:
        return {"task_id": task_id, "status": "SUCCESS"}

@router.get("/results/{task_id}")
def get_results(task_id: str):
    result = storage.get_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found or not completed")
    elif isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=f"Task failed: {result['error']}")
    return result

@router.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None)
):
    body = await request.body()
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")

    if not secret or not verify_github_signature(secret, body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()
    action = payload.get("action")

    if payload.get("pull_request") and action in ["opened", "synchronize"]:
        pr = payload["pull_request"]
        repo_url = pr["base"]["repo"]["html_url"]
        pr_number = pr["number"]
        github_token = None  # Optional

        task = analyze_pr_task.delay(repo_url, pr_number, github_token)
        return {"task_id": task.id}

    return {"message": "Event ignored"}
