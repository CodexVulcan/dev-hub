"""
conftest.py -- shared test fixtures.

Uses a single SQLite connection held open for the entire session so the
in-memory database (and its tables) persists across all test functions.
"""
import sys, os, json
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Create engine with a SINGLE persistent connection for the test session.
# "check_same_thread=False" is required for SQLite with FastAPI threads.
# We use connect_args + creator to reuse one connection object.
# ---------------------------------------------------------------------------
from sqlalchemy.pool import StaticPool

TEST_ENGINE = create_engine(
    "sqlite://",                      # in-memory
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,             # same connection every time -- tables persist
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def _override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import these AFTER engine is defined so imports do not trigger prod db setup
from backend.database import Base, get_db
from backend.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    from backend.models import teams, pipeline, debugging, review, testing, maintenance  # noqa
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture()
def client(tmp_path, _create_tables):
    app.dependency_overrides[get_db] = _override_get_db

    import backend.routers.mindmap as mm_router
    import backend.routers.dashboard as db_router

    orig_mm, orig_db = mm_router._DATA_FILE, db_router._DATA_FILE
    tmp_mm = str(tmp_path / "mindmap.json")
    tmp_db = str(tmp_path / "dashboard.json")
    with open(tmp_mm, "w") as f: json.dump({"nodes": [], "edges": []}, f)
    with open(tmp_db, "w") as f: json.dump({"cards": []}, f)
    mm_router._DATA_FILE = tmp_mm
    db_router._DATA_FILE = tmp_db

    with patch("backend.main.init_db"):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c

    app.dependency_overrides.clear()
    mm_router._DATA_FILE = orig_mm
    db_router._DATA_FILE = orig_db
