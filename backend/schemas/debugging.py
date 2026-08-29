from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

SEVERITY = Literal["critical", "major", "minor"]


class IssueInput(BaseModel):
    title:       str
    description: str = ""
    severity:    SEVERITY


class ReportCreate(BaseModel):
    title:  str
    issues: list[IssueInput]


class IssueResponse(BaseModel):
    id:            int
    title:         str
    description:   str
    severity:      str
    suggested_fix: str
    status:        str

    model_config = {"from_attributes": True}


class ReportResponse(BaseModel):
    id:         int
    title:      str
    issues:     list[IssueResponse] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReportsListResponse(BaseModel):
    reports: list[ReportResponse]
