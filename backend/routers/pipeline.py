"""
pipeline.py -- Pipeline Access module router.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.pipeline import PipelineProject, PipelineStage
from backend.schemas.pipeline import (
    ProjectCreate, StageUpdate,
    ProjectResponse, ProjectsListResponse, StageResponse, GithubSyncResponse
)
from backend.services.github_service import fetch_workflow_status

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])
STAGES = ["build", "test", "deploy"]

def _project_with_stages(project: PipelineProject, db: Session) -> dict:
    stages = db.query(PipelineStage).filter(PipelineStage.project_id == project.id).all()
    stage_map = {s.stage: s for s in stages}
    stage_list = []
    for name in STAGES:
        stage_list.append(stage_map[name] if name in stage_map else StageResponse(stage=name, status="pending"))
    return {
        "id": project.id, "name": project.name, "description": project.description,
        "github_owner": project.github_owner, "github_repo": project.github_repo,
        "stages": stage_list, "created_at": project.created_at,
    }

@router.get("/projects", response_model=ProjectsListResponse)
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(PipelineProject).order_by(PipelineProject.id).all()
    return {"projects": [_project_with_stages(p, db) for p in projects]}

@router.post("/projects", response_model=ProjectResponse, status_code=201)
def add_project(body: ProjectCreate, db: Session = Depends(get_db)):
    if db.query(PipelineProject).filter(PipelineProject.name == body.name).first():
        raise HTTPException(status_code=409, detail="Project name already exists")
    project = PipelineProject(name=body.name, description=body.description,
                               github_owner=body.github_owner, github_repo=body.github_repo)
    db.add(project)
    db.flush()
    for stage_name in STAGES:
        db.add(PipelineStage(project_id=project.id, stage=stage_name, status="pending"))
    db.commit()
    db.refresh(project)
    return _project_with_stages(project, db)

@router.patch("/projects/{project_id}/stage", response_model=ProjectResponse)
def update_stage(project_id: int, body: StageUpdate, db: Session = Depends(get_db)):
    project = db.query(PipelineProject).filter(PipelineProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    stage = db.query(PipelineStage).filter(
        PipelineStage.project_id == project_id, PipelineStage.stage == body.stage).first()
    if stage:
        stage.status = body.status
    else:
        db.add(PipelineStage(project_id=project_id, stage=body.stage, status=body.status))
    db.commit()
    return _project_with_stages(project, db)

@router.get("/projects/{project_id}/github-sync", response_model=GithubSyncResponse)
async def github_sync(
    project_id: int,
    owner: str = Query(""),
    repo: str = Query(""),
    db: Session = Depends(get_db),
):
    project = db.query(PipelineProject).filter(PipelineProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    resolved_owner = owner or project.github_owner or ""
    resolved_repo  = repo  or project.github_repo  or ""
    if not resolved_owner or not resolved_repo:
        return GithubSyncResponse(project_id=project_id, stage="build", status="pending", reason="owner_or_repo_missing")
    result = await fetch_workflow_status(resolved_owner, resolved_repo)
    stage = db.query(PipelineStage).filter(
        PipelineStage.project_id == project_id, PipelineStage.stage == "build").first()
    if stage and result["status"] != "pending":
        stage.status = result["status"]
        db.commit()
    return GithubSyncResponse(project_id=project_id, stage="build", status=result["status"], reason=result.get("reason"))