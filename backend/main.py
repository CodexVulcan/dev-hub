"""
main.py — DevHub Platform FastAPI application entry point.

Start the server from the dev-hub/ directory:
    uvicorn backend.main:app --reload

Security note: this file never reads, logs, or exposes content from paths
matching .bobignore / .gitignore patterns (*.db, .env, *.key, *.pem,
secrets/, config/credentials.json).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

from backend.database import init_db, get_db

# -- Router imports ----------------------------------------------------------
from backend.routers import (
    pulse,
    teams,
    pipeline,
    mindmap,
    dashboard,
    analyzer,
    debugging,
    review,
    testing,
    deployment,
    maintenance,
)


# -- Lifespan: initialise DB tables on startup -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


# -- Application factory -----------------------------------------------------
app = FastAPI(
    title="DevHub Platform",
    description="Integrated developer team platform — 10 workflow modules.",
    version="0.1.0",
    lifespan=lifespan,
)

# -- CORS — localhost only (development) -------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Register all module routers ---------------------------------------------
app.include_router(teams.router)
app.include_router(pipeline.router)
app.include_router(mindmap.router)
app.include_router(dashboard.router)
app.include_router(analyzer.router)
app.include_router(debugging.router)
app.include_router(review.router)
app.include_router(testing.router)
app.include_router(deployment.router)
app.include_router(maintenance.router)
app.include_router(pulse.router)


# -- Health check ------------------------------------------------------------
@app.get("/api/health", tags=["system"])
async def health():
    """Liveness probe — returns OK when the server is running."""
    return {"status": "ok", "platform": "DevHub"}


# -- Platform export ----------------------------------------------------------
@app.get("/api/export", tags=["system"])
async def export_state(db: Session = Depends(get_db)):
    """
    Export a full JSON snapshot of all platform state across every module.
    Excludes: DB file path, secrets, tokens, environment variables.
    """
    from backend.services.export_service import export_platform_state
    return export_platform_state(db)


# -- Static file serving — frontend/ dir -------------------------------------
# Mounted LAST so API routes always take priority.
_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="frontend")
