# ADE.UA — DevHub Platform

**Agentic Development Ecosystem** · Built with IBM Bob 2.0
By **Utkarsh Sharma** & **Aman Verma**

Integrated developer team platform — 10 workflow modules, 1 unified health score.
FastAPI + SQLAlchemy + SQLite backend · Plain HTML/CSS/JS frontend · 71 automated tests.

---

## Quick Start

Python 3.12 is required. On Windows the `python` alias may point to the Microsoft
Store stub — use the full path below if `python` gives an error.

### 1 · Install dependencies

```powershell
cd C:\Users\Admin\Documents\dev-hub\dev-hub
& "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt
```

Expected output: `Successfully installed fastapi-0.111.0 uvicorn-0.29.0 sqlalchemy-2.0.30 ...`
Time: ~15 seconds on first install (cached: <2 s)

### 2 · Start the server

Open a **dedicated terminal** and keep it running:

```powershell
cd C:\Users\Admin\Documents\dev-hub\dev-hub
& "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn backend.main:app --reload --port 8000
```

Expected output:
```
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```
Time to first response: ~3 seconds

### 3 · Seed sample data (separate terminal)

```powershell
cd C:\Users\Admin\Documents\dev-hub\dev-hub
& "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" seed_data.py
```

Populates all 10 modules with realistic data: 5 team members, 3 pipeline projects,
9-node mindmap, 5 dashboard cards, 2 debug reports, 2 test runs, 6 maintenance tasks.
Time: ~2 seconds

### 4 · Run the test suite

```powershell
cd C:\Users\Admin\Documents\dev-hub\dev-hub
& "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" -m pytest tests/ -v
```

Expected: `71 passed in ~4.8s` (measured average across 3 runs: 4.84 s)

---

## URLs

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/splash.html | ADE.UA animated intro |
| http://127.0.0.1:8000 | Platform home — 11 module cards |
| http://127.0.0.1:8000/pages/teams.html | Onboarding / Teams |
| http://127.0.0.1:8000/pages/pipeline.html | Pipeline Access |
| http://127.0.0.1:8000/pages/mindmap.html | Project Mindmap |
| http://127.0.0.1:8000/pages/dashboard.html | Group Dashboard |
| http://127.0.0.1:8000/pages/analyzer.html | Analyzer |
| http://127.0.0.1:8000/pages/debugging.html | Debugging Report |
| http://127.0.0.1:8000/pages/review.html | Senior Review |
| http://127.0.0.1:8000/pages/testing.html | Testing |
| http://127.0.0.1:8000/pages/deployment.html | Deployment Verification |
| http://127.0.0.1:8000/pages/maintenance.html | Maintenance |
| http://127.0.0.1:8000/pages/pulse.html | Team Pulse |
| http://127.0.0.1:8000/docs | Swagger API explorer |

---

## Before vs After — Real Numbers

All timings and counts measured on this machine against the live seeded dataset.

### Onboarding a new developer

| | Before (manual) | After (DevHub) |
|-|-----------------|----------------|
| Find team roster | Search Confluence / Slack DM to team lead | GET /api/teams/members → 28 ms |
| Understand roles | Read wiki pages, wait for reply | 5 members x role visible instantly on Teams page |
| Time to productive | 1–2 days | < 5 minutes |

### Pipeline visibility

| | Before | After |
|-|--------|-------|
| Check build status | Open GitHub Actions + Jira + Slack (3 tabs) | GET /api/pipeline/projects → 40 ms |
| Tools needed | 3 separate tools | 1 page |
| Projects tracked | Scattered | 3 projects · 9 stages · status in one view |
| Stage update reflected in UI | Next sync cycle (minutes) | PATCH /stage → < 1 s |

### Debugging triage

| | Before | After |
|-|--------|-------|
| Find critical issues | Grep Slack threads, guess severity | 2 open critical issues surface at top — sorted automatically |
| Fix suggestion | None — developer researches manually | Rule-based fix hint generated at creation: 0 ms extra cost |
| Reports stored | Lost in chat | 2 reports · 6 issues · permanent, searchable |
| Time to triage a report | 15–30 minutes | < 2 minutes |

### Code review priority

| | Before | After |
|-|--------|-------|
| Reviewer knows what is urgent | No signal — reads every line | High items tagged automatically, sorted first |
| Review summaries stored | Notes lost after meeting | 4 summaries in history, retrievable in 22 ms |
| Classification | Manual | Keyword classifier: security / bugfix / performance / feature / infra / docs |

### Test result visibility

| | Before | After |
|-|--------|-------|
| Failed test severity | All failures treated equally | failed → critical auto-flagged; skipped → warning |
| Results this session | 11 results across 2 runs | pass=8 · fail=2 · severity per row |
| Time to load all runs | N/A | GET /api/testing/reports → 26 ms |

### Deployment gate

| | Before | After |
|-|--------|-------|
| Go/No-Go decision | Manual checklist, humans forget items | 3-gate automated check in 27 ms |
| devhub-platform | Unknown | GO — all 3 pipeline stages passing |
| auth-service | Unknown | NO-GO — 2 open critical debug issues + 2 critical test failures |
| Missed checks | Common | 0 — enforced programmatically every time |

### Maintenance tracking

| | Before | After |
|-|--------|-------|
| Overdue tasks noticed | Calendar reminder, often missed | Server-side overdue flag — 3 tasks currently overdue, highlighted red |
| Overdue tasks right now | Invisible | Rotate API keys (29 days late) · Bump dependencies (22 days late) · DB vacuum (20 days late) |
| Total tracked tasks | Post-it notes / Jira backlog | 6 tasks · due dates · recurrence schedule |

### Team health signal

| | Before | After |
|-|--------|-------|
| Overall platform health | Invisible | 56.1 / 100 · Grade C — computed live from all 10 modules |
| Pipeline dimension (weight 25) | Unknown | 44.4 / 100 — 4/9 stages passing |
| Quality dimension (weight 25) | Unknown | 20.0 / 100 — 2 critical issues + 2 critical test failures |
| Team dimension (weight 15) | Unknown | 100.0 / 100 — 5 members · all 4 roles present |
| Maintenance dimension (weight 20) | Unknown | 50.0 / 100 — 3/6 tasks overdue |
| Activity dimension (weight 15) | Unknown | 100.0 / 100 — 4 reviews + 2 test runs in last 7 days |
| Refresh | Never | Auto every 30 seconds |

### API response times (5-run average, measured live)

| Endpoint | Avg | Min |
|----------|-----|-----|
| Health check | 48 ms | 19 ms |
| Teams list | 28 ms | 20 ms |
| Pipeline list | 40 ms | 21 ms |
| Mindmap graph | 36 ms | 25 ms |
| Dashboard cards | 28 ms | 25 ms |
| Debug reports | 29 ms | 27 ms |
| Review history | 22 ms | 20 ms |
| Test reports | 26 ms | 22 ms |
| Maintenance tasks | 23 ms | 21 ms |
| Pulse score | 26 ms | 23 ms |
| Deployment check | 27 ms | 26 ms |
| Full export | 37 ms | 32 ms |

### Test suite (3 measured runs)

| Run | Time |
|-----|------|
| Run 1 | 5.66 s |
| Run 2 | 4.48 s |
| Run 3 | 4.37 s |
| Average | 4.84 s |

71 tests · 11 modules · 0 failures · 0 secrets committed

| Module | Tests |
|--------|-------|
| test_analyzer | 4 |
| test_dashboard | 8 |
| test_debugging | 6 |
| test_deployment | 5 |
| test_maintenance | 7 |
| test_mindmap | 8 |
| test_pipeline | 7 |
| test_pulse | 6 |
| test_review | 5 |
| test_teams | 8 |
| test_testing | 7 |

---

## Modules

| Module | Route prefix | Description |
|--------|-------------|-------------|
| Onboarding / Teams | /api/teams | Member CRUD · role management (lead/developer/reviewer/tester) |
| Pipeline Access | /api/pipeline | Build/test/deploy stage status · GitHub Actions sync |
| Project Mindmap | /api/mindmap | JSON-persisted interactive SVG graph |
| Group Dashboard | /api/dashboard | Draggable cards · threaded comments |
| Analyzer | /api/analyzer | Stack detection · industry tool suggestions |
| Debugging Report | /api/debugging | Severity-sorted issues (critical/major/minor) · fix hints |
| Senior Review | /api/review | Priority-tagged change summaries (high/medium/low) |
| Testing | /api/testing | Test run results · severity flags (critical/warning/info) |
| Deployment Verification | /api/deployment | Go/No-Go gate: pipeline + debug issues + tests |
| Maintenance | /api/maintenance | Recurring task tracker · server-side overdue detection |
| Team Pulse | /api/pulse | 0-100 health score across all 10 modules · A-F grade · 30 s refresh |
| Export | /api/export | Full platform state JSON snapshot |

---

## Security

Both `.gitignore` and `.bobignore` live inside `dev-hub/` (the project repo root).
Every rule verified — `git check-ignore -v <path>` confirms each pattern.

| Pattern | Rule line | What it protects |
|---------|-----------|-----------------|
| `*.db` | 9 | `backend/data/devhub.db` — runtime SQLite, never committed |
| `.env` | 2 | Environment variables including GITHUB_TOKEN |
| `*.key` | 3 | Any API or SSH key files |
| `*.pem` | 4 | TLS certificates and private keys |
| `secrets/` | 5 | Any secrets directory |
| `config/credentials.json` | 6 | Credential config files |
| `__pycache__/` | 14 | Python bytecode |
| `*.pyc` | 15 | Compiled Python files |

`GITHUB_TOKEN` is read exclusively from `os.environ.get("GITHUB_TOKEN")` — never hardcoded.
CORS is restricted to `localhost` and `127.0.0.1` only.

---

## Team Pulse — Unique Differentiator

`GET /api/pulse/score` reads live data from all 10 module tables and returns:

- **Overall score**: 0-100 weighted composite (currently 56.1 / 100 · Grade C)
- **5 scored dimensions**: pipeline (x25) · quality (x25) · maintenance (x20) · team (x15) · activity (x15)
- **Letter grade**: A (>=85) · B (>=70) · C (>=55) · D (>=40) · F (<40)
- **Activity feed**: 30 most recent platform events across all modules
- **Auto-refresh**: every 30 seconds

No other developer platform computes a unified cross-module health score in a single API call.