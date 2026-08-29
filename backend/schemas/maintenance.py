from pydantic import BaseModel
from typing import Literal, Optional
from datetime import date, datetime

CATEGORY   = Literal["dependency_update", "security_patch", "database_backup", "certificate_renewal", "code_audit", "other"]
RECURRENCE = Literal["none", "weekly", "monthly", "quarterly"]
STATUS     = Literal["pending", "completed"]


class TaskCreate(BaseModel):
    title:       str
    description: str = ""
    category:    CATEGORY = "other"
    due_date:    date
    recurrence:  RECURRENCE = "none"


class TaskUpdate(BaseModel):
    status:   Optional[STATUS] = None
    due_date: Optional[date] = None


class TaskResponse(BaseModel):
    id:          int
    title:       str
    description: str
    category:    str
    due_date:    date
    recurrence:  str
    status:      str
    overdue:     bool
    created_at:  Optional[datetime] = None

    model_config = {"from_attributes": True}


class TasksListResponse(BaseModel):
    tasks: list[TaskResponse]
