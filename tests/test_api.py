from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import hmac
import hashlib
import json
import os
from dotenv import load_dotenv
load_dotenv()

client = TestClient(app)

def test_analyze_pr_endpoint():
    response = client.post("/analyze-pr", json={
        "repo_url": "https://github.com/qdrant/qdrant/pull/6948",
        "pr_number": 6948
    })
    assert response.status_code == 200
    assert "task_id" in response.json()


def test_status_endpoint():
    # Mock a fake task ID that Celery doesn't know
    task_id = "fake-task-id"
    response = client.get(f"/status/{task_id}")
    assert response.status_code == 200
    assert response.json()["task_id"] == task_id


@patch("app.services.storage.get_result")
def test_results_endpoint(mock_get_result):
    mock_get_result.return_value = {
        "files": [{"name": "file.py", "issues": []}],
        "summary": {"total_files": 1, "total_issues": 0, "critical_issues": 0}
    }

    task_id = "abc123"
    response = client.get(f"/results/{task_id}")
    assert response.status_code == 200
    assert "files" in response.json()


# @patch("app.tasks.review.analyze_pr_task.delay")
# def test_webhook_valid_signature(mock_task):
#     # Set a known secret
#     secret = "testsecret"
#     os.environ["GITHUB_WEBHOOK_SECRET"] = secret

#     payload = {
#         "action": "opened",
#         "pull_request": {
#             "number": 1,
#             "base": {
#                 "repo": {
#                     "html_url": "https://github.com/user/repo"
#                 }
#             }
#         }
#     }
#     raw = json.dumps(payload).encode()
#     signature = hmac.new(secret.encode(), msg=raw, digestmod=hashlib.sha256).hexdigest()
#     headers = {
#         "X-Hub-Signature-256": f"sha256={signature}"
#     }

#     mock_task.return_value.id = "test-task-id"

#     response = client.post("/webhook", data=raw, headers=headers)
#     assert response.status_code == 200
#     assert "task_id" in response.json()


# def test_webhook_invalid_signature():
#     payload = {"action": "opened", "pull_request": {"number": 1, "base": {"repo": {"html_url": "https://github.com/user/repo"}}}}
#     raw = json.dumps(payload).encode()
#     headers = {
#         "X-Hub-Signature-256": "sha256=invalidsignature"
#     }

#     os.environ["GITHUB_WEBHOOK_SECRET"] = "testsecret"
#     response = client.post("/webhook", data=raw, headers=headers)
#     assert response.status_code == 403

