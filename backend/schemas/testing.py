from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

STATUS   = Literal["passed", "failed", "skipped", "error"]
SEVERITY = Literal["critical", "warning", "info"]


class TestResultInput(BaseModel):
    test_name: str
    status:    STATUS
    message:   str = ""
    severity:  SEVERITY = "info"


class TestRunCreate(BaseModel):
    test_suite: str
    results:    list[TestResultInput]


class TestResultResponse(BaseModel):
    id:        int
    test_name: str
    status:    str
    message:   str
    severity:  str

    model_config = {"from_attributes": True}


class TestRunResponse(BaseModel):
    id:         int
    test_suite: str
    results:    list[TestResultResponse] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TestRunsListResponse(BaseModel):
    reports: list[TestRunResponse]
