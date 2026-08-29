from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

STAGE_STATUS = Literal["passing", "failing", "running", "pending"]
STAGE_NAME   = Literal["build", "test", "deploy"]


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    github_owner: Optional[str] = None
    github_repo:  Optional[str] = None


class StageUpdate(BaseModel):
    stage:  STAGE_NAME
    status: STAGE_STATUS


class StageResponse(BaseModel):
    stage:      str
    status:     str
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id:           int
    name:         str
    description:  str
    github_owner: Optional[str] = None
    github_repo:  Optional[str] = None
    stages:       list[StageResponse] = []
    created_at:   Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProjectsListResponse(BaseModel):
    projects: list[ProjectResponse]


class GithubSyncResponse(BaseModel):
    project_id: int
    stage:      str
    status:     str
    reason:     Optional[str] = None
