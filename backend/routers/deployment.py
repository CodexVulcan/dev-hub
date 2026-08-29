"""
deployment.py — Deployment Verification module router.
Go/No-Go check: pipeline passing + no critical debug issues + no critical failing tests.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.pipeline import PipelineProject, PipelineStage
from backend.models.debugging import DebuggingIssue
from backend.models.testing import TestResult
from backend.schemas.deployment import DeploymentCheckResponse, DeploymentCheck

router = APIRouter(prefix="/api/deployment", tags=["deployment"])


@router.get("/check/{project_id}", response_model=DeploymentCheckResponse)
def check_deployment(project_id: int, db: Session = Depends(get_db)):
    project = db.query(PipelineProject).filter(PipelineProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    checks = []

    # -- Check 1: all pipeline stages passing -----------------------------
    stages = db.query(PipelineStage).filter(PipelineStage.project_id == project_id).all()
    non_passing = [s for s in stages if s.status != "passing"]
    if not stages:
        checks.append(DeploymentCheck(
            name="Pipeline stages",
            passed=False,
            detail="No pipeline stages configured for this project.",
        ))
    elif non_passing:
        names = ", ".join(f"{s.stage}={s.status}" for s in non_passing)
        checks.append(DeploymentCheck(
            name="Pipeline stages",
            passed=False,
            detail=f"Non-passing stages: {names}",
        ))
    else:
        checks.append(DeploymentCheck(
            name="Pipeline stages",
            passed=True,
            detail="All pipeline stages are passing.",
        ))

    # -- Check 2: no open critical debugging issues ---------------------
    critical_issues = db.query(DebuggingIssue).filter(
        DebuggingIssue.severity == "critical",
        DebuggingIssue.status == "open",
    ).count()
    if critical_issues > 0:
        checks.append(DeploymentCheck(
            name="Critical debug issues",
            passed=False,
            detail=f"{critical_issues} open critical debugging issue(s) must be resolved.",
        ))
    else:
        checks.append(DeploymentCheck(
            name="Critical debug issues",
            passed=True,
            detail="No open critical debugging issues.",
        ))

    # -- Check 3: no critical failing test results ---------------------
    critical_tests = db.query(TestResult).filter(
        TestResult.severity == "critical",
        TestResult.status.in_(["failed", "error"]),
    ).count()
    if critical_tests > 0:
        checks.append(DeploymentCheck(
            name="Critical test failures",
            passed=False,
            detail=f"{critical_tests} critical failing test(s) must be fixed before deploy.",
        ))
    else:
        checks.append(DeploymentCheck(
            name="Critical test failures",
            passed=True,
            detail="No critical failing tests.",
        ))

    go = all(c.passed for c in checks)
    return DeploymentCheckResponse(project_id=project_id, go=go, checks=checks)
