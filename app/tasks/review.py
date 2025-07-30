# from celery import shared_task
from app.services import github, storage
from app.api.agent.langgraph_agent import run_agent
from app.celery_worker import celery_app

@celery_app.task(name="analyze_pr_task")
def analyze_pr_task(repo_url, pr_number, github_token=None):
    print("Task analyze_pr_task is running")
    try:
        pr_files = github.get_pr_diff(repo_url, pr_number, github_token)
        analysis = run_agent(pr_files)
        print(" running agent for pr_files")
        storage.save_result(analyze_pr_task.request.id, analysis)
        return analysis
    except Exception as e:
        return {"error": str(e)}
