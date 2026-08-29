"""
database.py — SQLAlchemy engine, declarative base, session factory, and table creation.

The DB file is stored at backend/data/devhub.db.
This path matches the *.db exclusion in .bobignore and .gitignore — it is
runtime-only and must never be committed or read by Bob.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------------------------------------------------------------------
# Engine — file lives inside backend/data/ so it stays out of the repo root.
# The *.db glob in .gitignore/.bobignore covers this path.
# ---------------------------------------------------------------------------
_DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(_DB_DIR, exist_ok=True)
_DB_PATH = os.path.join(_DB_DIR, "devhub.db")

DATABASE_URL = f"sqlite:///{_DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ---------------------------------------------------------------------------
# Dependency — yields a DB session per request, always closes on teardown.
# ---------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# init_db — creates all tables whose models have been imported before this
# call. Called once at application startup from main.py.
# ---------------------------------------------------------------------------
def init_db() -> None:
    # Import every model module so SQLAlchemy knows about the tables before
    # create_all() runs.  Add new model imports here as modules are built.
    from backend.models import (  # noqa: F401
        teams,
        pipeline,
        debugging,
        review,
        testing,
        maintenance,
    )
    Base.metadata.create_all(bind=engine)
