from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal, Optional
from datetime import datetime

ROLES = Literal["lead", "developer", "reviewer", "tester"]


class MemberCreate(BaseModel):
    name: str
    email: str
    role: ROLES = "developer"

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()


class MemberRoleUpdate(BaseModel):
    role: ROLES


class MemberResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    joined_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MembersListResponse(BaseModel):
    members: list[MemberResponse]
