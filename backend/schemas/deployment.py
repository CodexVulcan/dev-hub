from pydantic import BaseModel


class DeploymentCheck(BaseModel):
    name:   str
    passed: bool
    detail: str


class DeploymentCheckResponse(BaseModel):
    project_id: int
    go:         bool
    checks:     list[DeploymentCheck]
