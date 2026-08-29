"""
seed_data.py - Populate DevHub Platform with realistic sample data.

Run from the dev-hub/ directory WHILE the server is running on port 8000:
    python seed_data.py

Idempotent: re-running is safe - duplicates are skipped.
Security: never references .bobignore patterns (*.db, .env, *.key, *.pem, secrets/).
"""
import json
from datetime import date, timedelta
import urllib.request, urllib.error

BASE = "http://127.0.0.1:8000"

def _req(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read()).get("detail","")
        except Exception:
            detail = ""
        return e.code, {"detail": detail}

def post(path, body): return _req("POST",  path, body)
def patch(path, body):return _req("PATCH", path, body)
def get(path):        return _req("GET",   path)

def ok(label, status, extra=""):
    icon = "OK" if status in (200, 201) else f"skip({status})"
    suffix = f" -- {extra}" if extra else ""
    print(f"  [{icon}]  {label}{suffix}")

today  = date.today()
past   = lambda d: (today - timedelta(days=d)).isoformat()
future = lambda d: (today + timedelta(days=d)).isoformat()

# ---------------------------------------------------------------------------
# 1. TEAMS
# ---------------------------------------------------------------------------
print("\n[1/10] Teams")
members = [
    {"name": "Utkarsh Sharma", "email": "utkarsh@adeua.dev", "role": "lead"},
    {"name": "Aman Verma",     "email": "aman@adeua.dev",    "role": "lead"},
    {"name": "Priya Patel",    "email": "priya@adeua.dev",   "role": "developer"},
    {"name": "Ravi Nair",      "email": "ravi@adeua.dev",    "role": "reviewer"},
    {"name": "Sara Khan",      "email": "sara@adeua.dev",    "role": "tester"},
]
for m in members:
    s, r = post("/api/teams/members", m)
    ok(m["name"], s, r.get("detail",""))

# ---------------------------------------------------------------------------
# 2. PIPELINE  (PATCH /projects/{id}/stage  -- note singular "stage")
# ---------------------------------------------------------------------------
print("\n[2/10] Pipeline")
projects = [
    {"name": "devhub-platform",  "description": "Core ADE.UA DevHub application"},
    {"name": "auth-service",     "description": "JWT authentication microservice"},
    {"name": "analytics-engine", "description": "Usage metrics aggregation service"},
]
stages_map = {
    "devhub-platform":  [("build","passed"),  ("test","passed"),  ("deploy","passed")],
    "auth-service":     [("build","passed"),  ("test","failed"),  ("deploy","pending")],
    "analytics-engine": [("build","running"), ("test","pending"), ("deploy","pending")],
}
for p in projects:
    s, resp = post("/api/pipeline/projects", p)
    ok(p["name"], s, resp.get("detail",""))
    pid = resp.get("id")
    if pid:
        for stage, status in stages_map[p["name"]]:
            s2, r2 = patch(f"/api/pipeline/projects/{pid}/stage",
                           {"stage": stage, "status": status})
            ok(f"  stage {stage}={status}", s2, r2.get("detail",""))

# ---------------------------------------------------------------------------
# 3. MINDMAP
# ---------------------------------------------------------------------------
print("\n[3/10] Mindmap")
nodes = [
    {"id": "root",     "label": "DevHub Platform", "x": 400, "y": 60,  "color": "#3b82d4"},
    {"id": "backend",  "label": "FastAPI Backend",  "x": 180, "y": 180, "color": "#7c5cd8"},
    {"id": "frontend", "label": "HTML/CSS/JS UI",   "x": 620, "y": 180, "color": "#7c5cd8"},
    {"id": "db",       "label": "SQLite DB",        "x": 80,  "y": 320, "color": "#e57c3c"},
    {"id": "routers",  "label": "11 Routers",       "x": 280, "y": 320, "color": "#e57c3c"},
    {"id": "pages",    "label": "11 Pages",         "x": 520, "y": 320, "color": "#e57c3c"},
    {"id": "pulse",    "label": "Team Pulse",       "x": 720, "y": 320, "color": "#22a06b"},
    {"id": "tests",    "label": "71 Tests",         "x": 180, "y": 460, "color": "#57606a"},
    {"id": "schemas",  "label": "Pydantic Schemas", "x": 380, "y": 460, "color": "#57606a"},
]
edges = [
    {"source":"root",    "target":"backend"},
    {"source":"root",    "target":"frontend"},
    {"source":"backend", "target":"db"},
    {"source":"backend", "target":"routers"},
    {"source":"frontend","target":"pages"},
    {"source":"frontend","target":"pulse"},
    {"source":"routers", "target":"tests"},
    {"source":"routers", "target":"schemas"},
]
for n in nodes:
    s, r = post("/api/mindmap/nodes", n)
    ok(n["label"], s, r.get("detail",""))
for e in edges:
    s, r = post("/api/mindmap/edges", e)
    ok(f"edge {e['source']}->{e['target']}", s, r.get("detail",""))

# ---------------------------------------------------------------------------
# 4. DASHBOARD
# ---------------------------------------------------------------------------
print("\n[4/10] Dashboard")
cards_data = [
    {"title":"Launch Checklist",       "body":"Splash done. 71 tests pass. Server live. Seed loaded.",        "color":"#d1fae5","x":40, "y":40, "author":"Utkarsh","comments":[{"text":"Deployment check is green!","author":"Aman"}]},
    {"title":"Idea: Dark/Light Toggle","body":"Add theme switch in sidebar. CSS variables make this easy.",   "color":"#fef3c7","x":340,"y":40, "author":"Priya",  "comments":[{"text":"CSS variables make this trivial","author":"Ravi"}]},
    {"title":"Bug: Pipeline timeout",  "body":"GitHub Actions sync times out on large repos. Paginate.",      "color":"#fee2e2","x":640,"y":40, "author":"Sara",   "comments":[{"text":"Set httpx timeout=30","author":"Aman"}]},
    {"title":"Roadmap Q3",             "body":"1.OAuth login  2.PDF export  3.Slack  4.Multi-team spaces",    "color":"#ede9fe","x":40, "y":320,"author":"Aman",   "comments":[]},
    {"title":"Code Review Guidelines", "body":"Max PR 400 lines. 1 reviewer + green CI. Conventional commits.","color":"#e0f2fe","x":340,"y":320,"author":"Ravi","comments":[{"text":"Add to CONTRIBUTING.md","author":"Priya"}]},
]
for c in cards_data:
    comments = c.pop("comments")
    s, resp = post("/api/dashboard/cards", c)
    ok(c["title"], s, resp.get("detail",""))
    cid = resp.get("id")
    if cid:
        for comment in comments:
            s2, r2 = post(f"/api/dashboard/cards/{cid}/comments", comment)
            ok(f"  comment by {comment['author']}", s2, r2.get("detail",""))

# ---------------------------------------------------------------------------
# 5. ANALYZER  (file_listing=str, tech_hints=str)
# ---------------------------------------------------------------------------
print("\n[5/10] Analyzer")
s, r = post("/api/analyzer/analyze", {
    "file_listing": "backend/main.py backend/database.py requirements.txt frontend/index.html frontend/static/style.css frontend/static/app.js tests/conftest.py tests/test_teams.py README.md .github/workflows/ci.yml",
    "tech_hints": "FastAPI SQLAlchemy SQLite pytest GitHub Actions CI/CD Docker"
})
ok("analyzer scan", s, r.get("detail",""))

# ---------------------------------------------------------------------------
# 6. DEBUGGING  (POST /api/debugging/report  -- singular)
# ---------------------------------------------------------------------------
print("\n[6/10] Debugging")
debug_reports = [
    {"title": "Sprint 4 Pre-release", "issues": [
        {"title":"SQL injection in search",   "description":"User input to raw SQL without parameterisation.","severity":"critical","suggested_fix":"Use SQLAlchemy ORM.",         "status":"open"},
        {"title":"Memory leak in WS handler", "description":"Listeners not cleaned on disconnect.",           "severity":"major",   "suggested_fix":"Cleanup in disconnect handler.","status":"open"},
        {"title":"Wrong HTTP 200 on create",  "description":"POST returns 200 instead of 201.",               "severity":"minor",   "suggested_fix":"Add status_code=201.",          "status":"resolved"},
    ]},
    {"title": "Auth Service Security Audit", "issues": [
        {"title":"JWT secret hardcoded",   "description":"Secret literal in auth_config.py line 14.",  "severity":"critical","suggested_fix":"Move to JWT_SECRET env var.",      "status":"open"},
        {"title":"Token expiry 30 days",   "description":"Access tokens valid 30 days.",               "severity":"major",   "suggested_fix":"15 min access + 7 day refresh.",   "status":"open"},
        {"title":"No rate limit on /login","description":"No brute-force protection on login.",        "severity":"major",   "suggested_fix":"slowapi 5 req/min per IP.",        "status":"open"},
    ]},
]
for r_ in debug_reports:
    s, r = post("/api/debugging/report", r_)
    ok(r_["title"], s, r.get("detail",""))

# ---------------------------------------------------------------------------
# 7. SENIOR REVIEW
# ---------------------------------------------------------------------------
print("\n[7/10] Senior Review")
reviews = [
    "Fixed critical SQL injection in search endpoint; Patched JWT secret exposure; Added rate limiting to /login; Fixed WebSocket memory leak; Refactored pipeline sync to paginate; Updated README; Bumped fastapi 0.111.0 security patch; Added 71 unit tests; Performance: reduced DB queries 40 percent via eager loading; Fixed typo in dashboard label",
    "New feature: Team Pulse health score dashboard; Added parallel subagent tasks in analyzer; Implemented export_service snapshot; Added GitHub Actions sync endpoint; Deployment: verified go/no-go logic; Refactor: shared auth middleware; Bug: fixed overdue flag timezone mismatch in maintenance",
]
for i, text in enumerate(reviews, 1):
    s, r = post("/api/review/summarize", {"changes_text": text})
    ok(f"review summary #{i}", s, r.get("detail",""))

# ---------------------------------------------------------------------------
# 8. TESTING  (POST /api/testing/results)
# ---------------------------------------------------------------------------
print("\n[8/10] Testing")
runs = [
    {"test_suite": "DevHub Backend Full Suite", "results": [
        {"test_name":"test_add_member_happy",        "status":"passed", "message":""},
        {"test_name":"test_pipeline_stage_update",   "status":"passed", "message":""},
        {"test_name":"test_deployment_check_go",     "status":"passed", "message":""},
        {"test_name":"test_pulse_score_empty_db",    "status":"passed", "message":""},
        {"test_name":"test_analyzer_python_project", "status":"passed", "message":""},
        {"test_name":"test_debugging_severity_sort", "status":"passed", "message":""},
    ]},
    {"test_suite": "Auth Service Integration Tests", "results": [
        {"test_name":"test_login_valid_credentials", "status":"passed",  "message":""},
        {"test_name":"test_token_expiry_enforced",   "status":"failed",  "message":"AssertionError: expected 401 but got 200"},
        {"test_name":"test_refresh_token_rotation",  "status":"failed",  "message":"AttributeError: NoneType has no refresh_token"},
        {"test_name":"test_rate_limit_login",        "status":"skipped", "message":"slowapi not installed in test env"},
        {"test_name":"test_jwt_secret_from_env",     "status":"passed",  "message":""},
    ]},
]
for r_ in runs:
    s, r = post("/api/testing/results", r_)
    ok(r_["test_suite"], s, r.get("detail",""))

# ---------------------------------------------------------------------------
# 9. MAINTENANCE  (category must be one of the Literal enum values)
# ---------------------------------------------------------------------------
print("\n[9/10] Maintenance")
tasks = [
    {"title":"Bump Python dependencies",         "description":"pip-audit + pip install -U; pin in requirements.txt","category":"dependency_update",    "due_date":past(3),    "recurrence":"monthly"},
    {"title":"Rotate API keys",                  "description":"Regenerate GitHub token and any external API keys",  "category":"security_patch",       "due_date":past(10),   "recurrence":"quarterly"},
    {"title":"Database vacuum and integrity check","description":"PRAGMA integrity_check; VACUUM on SQLite DB",      "category":"database_backup",      "due_date":past(1),    "recurrence":"monthly"},
    {"title":"Review open debugging issues",     "description":"Triage open issues; close resolved; re-prioritise", "category":"code_audit",           "due_date":future(2),  "recurrence":"weekly"},
    {"title":"Update Docker base image",         "description":"Pull python:3.12-slim; rebuild and smoke test",      "category":"other",                "due_date":future(7),  "recurrence":"monthly"},
    {"title":"Generate code coverage report",    "description":"pytest --cov=backend and publish to team channel",   "category":"code_audit",           "due_date":future(14), "recurrence":"weekly"},
]
for t in tasks:
    s, r = post("/api/maintenance/tasks", t)
    ok(t["title"], s, r.get("detail",""))

# ---------------------------------------------------------------------------
# 10. DEPLOYMENT CHECK  (go: bool, checks: list)
# ---------------------------------------------------------------------------
print("\n[10/10] Deployment Check")
s, projects_resp = get("/api/pipeline/projects")
if s == 200:
    target = next((p for p in projects_resp.get("projects",[]) if p["name"]=="devhub-platform"), None)
    if target:
        s2, check = get(f"/api/deployment/check/{target['id']}")
        go = check.get("go")
        checks = check.get("checks", [])
        verdict = "GO" if go else "NO-GO"
        failed  = [c["name"] for c in checks if not c.get("passed")]
        detail  = ("; ".join(failed)) if failed else "all checks passed"
        ok(f"go/no-go -> {verdict}  ({detail})", s2)
    else:
        print("  project not found - skipping")
else:
    print(f"  pipeline list failed ({s})")

print("\nSeed complete. Open http://127.0.0.1:8000 to explore the platform.\n")