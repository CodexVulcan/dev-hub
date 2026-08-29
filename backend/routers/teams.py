"""
teams.py — Onboarding / Teams module router.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.teams import Member
from backend.schemas.teams import (
    MemberCreate, MemberRoleUpdate, MemberResponse, MembersListResponse
)

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("/members", response_model=MembersListResponse)
def list_members(db: Session = Depends(get_db)):
    members = db.query(Member).order_by(Member.joined_at).all()
    return {"members": members}


@router.post("/members", response_model=MemberResponse, status_code=201)
def add_member(body: MemberCreate, db: Session = Depends(get_db)):
    existing = db.query(Member).filter(Member.email == body.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    member = Member(name=body.name, email=body.email, role=body.role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/members/{member_id}", status_code=204)
def remove_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()


@router.patch("/members/{member_id}/role", response_model=MemberResponse)
def update_member_role(member_id: int, body: MemberRoleUpdate, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    member.role = body.role
    db.commit()
    db.refresh(member)
    return member
