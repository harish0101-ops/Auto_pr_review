# 🤖 Autonomous Code Review Agent

AI-powered code reviewer for GitHub pull requests. Asynchronously processes PR diffs using a LangGraph-based agent pipeline and provides structured feedback.

## ✅ Features

- FastAPI REST API
- Async task queue with Celery + Redis
- LangGraph-based agent with LLM reasoning
- Structured results with file-level issues
- Docker + `.env` support
- Test suite with pytest



docker-compose down --volumes --rmi all
docker builder prune -f
docker-compose build --no-cache
docker-compose up