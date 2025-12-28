# Python Full-Stack Project Template

A practical full-stack template for FastAPI + React with optional data services and local LLM support via Ollama. This repo is designed to be cloned and run with Docker Compose.

## Quick Start

### Prerequisites
- Docker 24+ and Docker Compose 2.0+
- Make (optional)

### 1) Clone
```bash
git clone https://github.com/<your-username>/python-project-template.git
cd python-project-template
```

### 2) Configure
```bash
cp .env.example .env
```
Edit `.env` to add API keys if you want Gemini or other providers. (Ollama runs locally.)

### 3) Start the Stack

**Full Setup (databases + frontend + nginx + Ollama; no Celery)**
```bash
./scripts/quick-start.sh
# or
make dev
```

**Minimal Setup (backend + Postgres + Redis)**
```bash
docker compose -f docker-compose.minimal.yml up
```

### Access
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend (Vite dev): http://localhost:5173
- Ollama: http://localhost:11434

## Notes on Auth/Admin

Authentication and admin endpoints were removed from the backend. The frontend still includes login/admin pages, but they do not function until auth is reintroduced.

## Feature Flags (Build-Time)

Edit `features.env` before startup to enable/disable services. Run `make dev` or `scripts/generate-profiles.sh` to apply profiles.

## LLM Smoke Tests

**Gemini (Google)**
```bash
docker compose exec backend python - <<'PY'
import asyncio
from app.helpers.llm.gemini_client import gemini_client
async def main():
    result = await gemini_client.generate_content("Say hello from the template.")
    print(result["content"])
asyncio.run(main())
PY
```

**Ollama (qwen2.5:7b)**
```bash
docker compose exec backend curl -s -X POST http://ollama:11434/api/generate \
  -d '{"model":"qwen2.5:7b","prompt":"Say hello"}'
```

## Testing

Test runners are wired, but the test suites are currently empty:
- Backend: `docker compose exec backend pytest -v`
- Frontend: `docker compose exec frontend npm test -- --run`

## Project Structure (High-Level)

- `backend/` FastAPI app, helpers, services, tasks
- `frontend/` React + Vite app
- `docker-compose.yml` base compose (profiles for optional services)
- `features.env` build-time service toggles
- `scripts/` helper scripts (profiles, quick start)

## Connect to GitHub and Push

### Option A: GitHub CLI
```bash
git init
git add .
git commit -m "Initial commit"
gh repo create <repo-name> --public --source=. --remote=origin --push
```

### Option B: GitHub Web + Git
1. Create a new repo in GitHub (no README/license).
2. Set remote and push:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin git@github.com:<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```
