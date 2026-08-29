"""
testing.py -- Testing module router.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.testing import TestRun, TestResult
from backend.schemas.testing import TestRunCreate, TestRunResponse, TestRunsListResponse

router = APIRouter(prefix="/api/testing", tags=["testing"])

_STATUS_SEVERITY = {"failed": "critical", "error": "critical", "skipped": "warning", "passed": "info"}

def _auto_severity(status: str) -> str:
    return _STATUS_SEVERITY.get(status, "info")

def _build_run_response(run: TestRun, results: list) -> dict:
    return {"id": run.id, "test_suite": run.test_suite, "results": results, "created_at": run.created_at}

@router.post("/results", response_model=TestRunResponse, status_code=201)
def submit_results(body: TestRunCreate, db: Session = Depends(get_db)):
    run = TestRun(test_suite=body.test_suite)
    db.add(run)
    db.flush()
    result_rows = []
    for r in body.results:
        # Use caller-supplied severity unless it is the default "info" -- then auto-derive from status
        severity = r.severity if r.severity != "info" else _auto_severity(r.status)
        row = TestResult(run_id=run.id, test_name=r.test_name, status=r.status, message=r.message, severity=severity)
        db.add(row)
        result_rows.append(row)
    db.commit()
    db.refresh(run)
    for row in result_rows:
        db.refresh(row)
    return _build_run_response(run, result_rows)

@router.get("/reports", response_model=TestRunsListResponse)
def list_reports(db: Session = Depends(get_db)):
    runs = db.query(TestRun).order_by(TestRun.created_at.desc()).all()
    return {"reports": [_build_run_response(r, db.query(TestResult).filter(TestResult.run_id == r.id).all()) for r in runs]}

@router.get("/reports/{run_id}", response_model=TestRunResponse)
def get_report(run_id: int, db: Session = Depends(get_db)):
    run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    return _build_run_response(run, db.query(TestResult).filter(TestResult.run_id == run_id).all())