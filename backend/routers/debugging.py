"""
debugging.py — Debugging Report module router.
Severity-sorted issues with rule-based fix suggestions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.debugging import DebuggingReport, DebuggingIssue
from backend.schemas.debugging import (
    ReportCreate, ReportResponse, ReportsListResponse, IssueResponse
)

router = APIRouter(prefix="/api/debugging", tags=["debugging"])

_SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2}

_FIX_RULES = [
    (["null", "none", "undefined", "nonetype"],  "Check for null/None before dereferencing. Use guard clauses or optional chaining."),
    (["timeout", "timed out", "deadline"],       "Increase timeout limits or add retry logic with exponential backoff."),
    (["memory", "oom", "out of memory", "heap"], "Profile memory usage. Check for object leaks or unbounded data structures."),
    (["auth", "unauthori", "forbidden", "403"],  "Verify token/session validity. Check permission scopes and RBAC rules."),
    (["network", "connection", "refused", "dns"],"Check service availability. Add circuit breaker or fallback mechanism."),
    (["type", "typeerror", "cast", "cannot convert"], "Validate input types at the boundary. Use stricter type annotations."),
    (["import", "module not found", "cannot find"], "Verify dependency is installed and import path is correct."),
    (["sql", "query", "database", "constraint"],  "Review query logic. Check for missing indexes or constraint violations."),
    (["race", "concurrency", "deadlock", "lock"], "Add synchronisation primitives. Review shared state access patterns."),
    (["key", "keyerror", "attribute", "attributeerror"], "Validate dictionary keys/object attributes before access."),
]

def _suggest_fix(title: str, description: str) -> str:
    text = (title + " " + description).lower()
    for keywords, fix in _FIX_RULES:
        if any(kw in text for kw in keywords):
            return fix
    return "Review the error context, add logging around the failure site, and isolate the minimal reproduction case."


def _to_response(report: DebuggingReport, issues: list) -> dict:
    sorted_issues = sorted(issues, key=lambda i: _SEVERITY_ORDER.get(i.severity, 99))
    return {
        "id": report.id,
        "title": report.title,
        "issues": sorted_issues,
        "created_at": report.created_at,
    }


@router.post("/report", response_model=ReportResponse, status_code=201)
def create_report(body: ReportCreate, db: Session = Depends(get_db)):
    report = DebuggingReport(title=body.title)
    db.add(report)
    db.flush()
    issues = []
    for inp in body.issues:
        fix = _suggest_fix(inp.title, inp.description)
        issue = DebuggingIssue(
            report_id=report.id,
            title=inp.title,
            description=inp.description,
            severity=inp.severity,
            suggested_fix=fix,
        )
        db.add(issue)
        issues.append(issue)
    db.commit()
    db.refresh(report)
    for i in issues:
        db.refresh(i)
    return _to_response(report, issues)


@router.get("/reports", response_model=ReportsListResponse)
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(DebuggingReport).order_by(DebuggingReport.created_at.desc()).all()
    result = []
    for r in reports:
        issues = db.query(DebuggingIssue).filter(DebuggingIssue.report_id == r.id).all()
        result.append(_to_response(r, issues))
    return {"reports": result}


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(DebuggingReport).filter(DebuggingReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    issues = db.query(DebuggingIssue).filter(DebuggingIssue.report_id == report_id).all()
    return _to_response(report, issues)


@router.patch("/issues/{issue_id}/resolve", status_code=200)
def resolve_issue(issue_id: int, db: Session = Depends(get_db)):
    """Mark a debugging issue as resolved."""
    issue = db.query(DebuggingIssue).filter(DebuggingIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.status = "resolved"
    db.commit()
    return {"id": issue_id, "status": "resolved"}
