# ADE.UA — DevHub Platform
**Agentic Development Ecosystem** by Utkarsh & Aman

Integrated developer team platform — 10 workflow modules built with FastAPI + SQLAlchemy + SQLite.

## First-time Setup

Python 3.12 must be installed.
On Windows the system `python` alias may point to the Microsoft Store stub.
Use the full path below if `python` is not found.

```powershell
# From the dev-hub/ directory:
& "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt
```

## Run

```powershell
# 1. Start the server (from dev-hub/ directory):
& "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn backend.main:app --reload --port 8000

# 2. (Optional) Seed sample data while server is running:
& "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" seed_data.py

# 3. Run tests:
& "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" -m pytest tests/ -v
```

Then open:
- **http://127.0.0.1:8000/splash.html** — ADE.UA animated intro
- **http://127.0.0.1:8000** — Platform home
- **http://127.0.0.1:8000/docs** — Swagger API explorer

## Team Pulse ⭐ (unique differentiator)

`/api/pulse/score` reads all 10 module tables and returns a 0–100 weighted health score
with a letter grade (A–F), 5 scored dimensions, and a 30-event activity feed.
Auto-refreshes every 30 seconds. This is the competition differentiator showing
cross-module agentic awareness in a single live dashboard.

## Modules

| Module | Route prefix | Description |
|--------|-------------|-------------|
| Onboarding / Teams | /api/teams | Member CRUD, role management |
| Pipeline Access | /api/pipeline | Build/test/deploy stage status + GitHub Actions sync |
| Project Mindmap | /api/mindmap | JSON-persisted interactive graph |
| Group Dashboard | /api/dashboard | Draggable cards + comments |
| Analyzer | /api/analyzer | Stack detection + tool suggestions |
| Debugging Report | /api/debugging | Severity-sorted issues + fix hints |
| Senior Review | /api/review | Priority-tagged change summaries |
| Testing | /api/testing | Structured test results viewer |
| Deployment Verification | /api/deployment | Go/No-Go cross-module check |
| Maintenance | /api/maintenance | Recurring tasks + overdue detection |
| Export | /api/export | Full platform state JSON snapshot |

## Security

- .env, *.key, *.pem, secrets/, config/credentials.json excluded via .gitignore and .bobignore
- SQLite DB (backend/data/devhub.db) is runtime-only, excluded via *.db
- GitHub token read from GITHUB_TOKEN env var only -- never hardcoded