"""
export_service.py — Platform-wide state snapshot exporter.

Queries every module table and returns a unified JSON-serialisable dict.
Security: DB file path, tokens, and env vars are never included in the export.
"""
import json
from datetime import date, datetime
from sqlalchemy.orm import Session


def _serialise(obj):
    """JSON-safe serialiser for dates/datetimes."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serialisable")


def export_platform_state(db: Session) -> dict:
    """
    Return a full platform snapshot as a plain dict (JSON-serialisable).
    Excludes: DB file path, secrets, tokens.
    """
    from backend.models.teams       import Member
    from backend.models.pipeline    import PipelineProject, PipelineStage
    from backend.models.debugging   import DebuggingReport, DebuggingIssue
    from backend.models.review      import ReviewSummary
    from backend.models.testing     import TestRun, TestResult
    from backend.models.maintenance import MaintenanceTask

    def rows(model):
        return [
            {c.name: getattr(row, c.name) for c in model.__table__.columns}
            for row in db.query(model).all()
        ]

    snapshot = {
        "teams":       {"members": rows(Member)},
        "pipeline":    {"projects": rows(PipelineProject), "stages": rows(PipelineStage)},
        "debugging":   {"reports": rows(DebuggingReport), "issues": rows(DebuggingIssue)},
        "review":      {"summaries": rows(ReviewSummary)},
        "testing":     {"runs": rows(TestRun), "results": rows(TestResult)},
        "maintenance": {"tasks": rows(MaintenanceTask)},
    }

    # Round-trip through json to coerce dates/datetimes to strings
    return json.loads(json.dumps(snapshot, default=_serialise))
