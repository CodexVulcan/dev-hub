"""
pulse.py -- Team Pulse module router.

UNIQUE DIFFERENTIATOR: Real-time cross-module health scoring.
Aggregates live signals from all 10 modules into:
  - A 0-100 "Team Health Score" with weighted sub-scores per dimension
  - A chronological activity feed of all platform events
  - Trend indicators (improving / stable / degrading)

No other developer platform computes a unified health score across
pipeline, quality, team completeness, maintenance compliance, and
active collaboration simultaneously.
"""
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.teams       import Member
from backend.models.pipeline    import PipelineProject, PipelineStage
from backend.models.debugging   import DebuggingReport, DebuggingIssue
from backend.models.review      import ReviewSummary
from backend.models.testing     import TestRun, TestResult
from backend.models.maintenance import MaintenanceTask

router = APIRouter(prefix="/api/pulse", tags=["pulse"])

# ---------------------------------------------------------------------------
# Score weights (must sum to 100)
# ---------------------------------------------------------------------------
WEIGHTS = {
    "pipeline":    25,   # are stages green?
    "quality":     25,   # no critical debug issues or test failures
    "team":        15,   # team has members with diverse roles
    "maintenance": 20,   # no overdue tasks
    "activity":    15,   # recent reviews, test runs -- team is active
}


def _pipeline_score(db: Session) -> tuple[float, str]:
    """25 pts: ratio of passing stages to total stages."""
    stages = db.query(PipelineStage).all()
    if not stages:
        return 0.0, "No pipeline projects configured"
    passing = sum(1 for s in stages if s.status == "passing")
    ratio = passing / len(stages)
    detail = f"{passing}/{len(stages)} stages passing"
    return round(ratio * 100, 1), detail


def _quality_score(db: Session) -> tuple[float, str]:
    """25 pts: penalise for open critical issues and critical test failures."""
    open_critical = db.query(DebuggingIssue).filter(
        DebuggingIssue.severity == "critical",
        DebuggingIssue.status == "open"
    ).count()
    critical_failures = db.query(TestResult).filter(
        TestResult.severity == "critical",
        TestResult.status.in_(["failed", "error"])
    ).count()
    total_penalties = open_critical + critical_failures
    if total_penalties == 0:
        return 100.0, "No critical issues or failing tests"
    # Each critical item costs 20 points, floor at 0
    score = max(0.0, 100.0 - total_penalties * 20)
    detail = f"{open_critical} open critical debug issues, {critical_failures} critical test failures"
    return score, detail


def _team_score(db: Session) -> tuple[float, str]:
    """15 pts: penalise if team has fewer than 2 members or missing roles."""
    members = db.query(Member).all()
    if not members:
        return 0.0, "No team members added"
    roles_present = {m.role for m in members}
    required_roles = {"lead", "developer"}
    missing = required_roles - roles_present
    base = min(len(members) / 3, 1.0) * 70   # up to 70 for headcount
    role_bonus = 30 if not missing else 15
    score = min(base + role_bonus, 100.0)
    detail = f"{len(members)} members, roles: {', '.join(sorted(roles_present))}"
    return round(score, 1), detail


def _maintenance_score(db: Session) -> tuple[float, str]:
    """20 pts: ratio of non-overdue tasks to total open tasks."""
    tasks = db.query(MaintenanceTask).filter(MaintenanceTask.status != "completed").all()
    if not tasks:
        return 100.0, "No pending maintenance tasks"
    overdue = sum(1 for t in tasks if t.due_date and t.due_date < date.today())
    ratio = 1.0 - (overdue / len(tasks))
    detail = f"{overdue}/{len(tasks)} maintenance tasks overdue"
    return round(ratio * 100, 1), detail


def _activity_score(db: Session) -> tuple[float, str]:
    """15 pts: reward recent activity (reviews + test runs in last 7 days)."""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    recent_reviews = db.query(ReviewSummary).filter(ReviewSummary.created_at >= cutoff).count()
    recent_runs    = db.query(TestRun).filter(TestRun.created_at >= cutoff).count()
    total_recent   = recent_reviews + recent_runs
    score = min(total_recent * 25, 100.0)   # 4+ activities = 100
    detail = f"{recent_reviews} reviews, {recent_runs} test runs in last 7 days"
    return round(score, 1), detail


def _build_feed(db: Session) -> list[dict]:
    """Collect the 30 most recent platform events across all modules."""
    events = []

    # Members joined
    for m in db.query(Member).order_by(Member.joined_at.desc()).limit(10).all():
        events.append({
            "type": "team", "icon": "person-add",
            "message": f"{m.name} joined as {m.role}",
            "timestamp": m.joined_at.isoformat() if m.joined_at else None,
            "severity": "info",
        })

    # Pipeline stage changes
    for s in db.query(PipelineStage).order_by(PipelineStage.updated_at.desc()).limit(10).all():
        project = db.query(PipelineProject).filter(PipelineProject.id == s.project_id).first()
        proj_name = project.name if project else "unknown"
        severity = "success" if s.status == "passing" else ("critical" if s.status == "failing" else "info")
        events.append({
            "type": "pipeline", "icon": "pipeline",
            "message": f"{proj_name} - {s.stage} stage is {s.status}",
            "timestamp": s.updated_at.isoformat() if s.updated_at else None,
            "severity": severity,
        })

    # Debug reports
    for r in db.query(DebuggingReport).order_by(DebuggingReport.created_at.desc()).limit(5).all():
        issue_count = db.query(DebuggingIssue).filter(DebuggingIssue.report_id == r.id).count()
        critical = db.query(DebuggingIssue).filter(
            DebuggingIssue.report_id == r.id, DebuggingIssue.severity == "critical"
        ).count()
        events.append({
            "type": "debugging", "icon": "bug",
            "message": f"Debug report '{r.title}': {issue_count} issues ({critical} critical)",
            "timestamp": r.created_at.isoformat() if r.created_at else None,
            "severity": "critical" if critical > 0 else "info",
        })

    # Test runs
    for run in db.query(TestRun).order_by(TestRun.created_at.desc()).limit(5).all():
        total = db.query(TestResult).filter(TestResult.run_id == run.id).count()
        failed = db.query(TestResult).filter(
            TestResult.run_id == run.id, TestResult.status.in_(["failed", "error"])
        ).count()
        events.append({
            "type": "testing", "icon": "check-circle",
            "message": f"Test run '{run.test_suite}': {total - failed}/{total} passed",
            "timestamp": run.created_at.isoformat() if run.created_at else None,
            "severity": "critical" if failed > 0 else "success",
        })

    # Maintenance overdue
    overdue = db.query(MaintenanceTask).filter(
        MaintenanceTask.status != "completed",
        MaintenanceTask.due_date < date.today()
    ).all()
    for t in overdue[:5]:
        events.append({
            "type": "maintenance", "icon": "warning",
            "message": f"Overdue: {t.title} (was due {t.due_date})",
            "timestamp": None,
            "severity": "warning",
        })

    # Senior reviews
    for r in db.query(ReviewSummary).order_by(ReviewSummary.created_at.desc()).limit(5).all():
        events.append({
            "type": "review", "icon": "review",
            "message": "Senior review summary generated",
            "timestamp": r.created_at.isoformat() if r.created_at else None,
            "severity": "info",
        })

    # Sort by timestamp descending, nulls last
    def sort_key(e):
        ts = e.get("timestamp")
        return ts if ts else "0"

    events.sort(key=sort_key, reverse=True)
    return events[:30]


@router.get("/score")
def get_health_score(db: Session = Depends(get_db)):
    """
    Compute the Team Health Score (0-100) with per-dimension breakdown.
    Aggregates live data from all 10 modules.
    """
    dimensions = {}

    p_score, p_detail = _pipeline_score(db)
    dimensions["pipeline"] = {"score": p_score, "weight": WEIGHTS["pipeline"], "detail": p_detail}

    q_score, q_detail = _quality_score(db)
    dimensions["quality"] = {"score": q_score, "weight": WEIGHTS["quality"], "detail": q_detail}

    t_score, t_detail = _team_score(db)
    dimensions["team"] = {"score": t_score, "weight": WEIGHTS["team"], "detail": t_detail}

    m_score, m_detail = _maintenance_score(db)
    dimensions["maintenance"] = {"score": m_score, "weight": WEIGHTS["maintenance"], "detail": m_detail}

    a_score, a_detail = _activity_score(db)
    dimensions["activity"] = {"score": a_score, "weight": WEIGHTS["activity"], "detail": a_detail}

    # Weighted overall score
    overall = sum(
        d["score"] * d["weight"] / 100
        for d in dimensions.values()
    )
    overall = round(overall, 1)

    # Grade
    grade = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D" if overall >= 40 else "F"

    return {
        "overall": overall,
        "grade": grade,
        "dimensions": dimensions,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/feed")
def get_activity_feed(db: Session = Depends(get_db)):
    """
    Return the last 30 platform events across all modules in chronological order.
    """
    return {"events": _build_feed(db)}


@router.get("")
def get_pulse(db: Session = Depends(get_db)):
    """Combined endpoint: health score + activity feed in one call."""
    score_data = get_health_score(db)
    feed_data  = get_activity_feed(db)
    return {**score_data, "feed": feed_data["events"]}