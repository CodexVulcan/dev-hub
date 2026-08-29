"""
maintenance.py — Maintenance module router.
Tracks recurring tasks with due dates; flags overdue items server-side.
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.maintenance import MaintenanceTask
from backend.schemas.maintenance import (
    TaskCreate, TaskUpdate, TaskResponse, TasksListResponse
)

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


def _add_overdue(task: MaintenanceTask) -> dict:
    overdue = (
        task.status != "completed" and
        task.due_date is not None and
        task.due_date < date.today()
    )
    return {
        "id": task.id, "title": task.title, "description": task.description,
        "category": task.category, "due_date": task.due_date,
        "recurrence": task.recurrence, "status": task.status,
        "overdue": overdue, "created_at": task.created_at,
    }


@router.get("/tasks", response_model=TasksListResponse)
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(MaintenanceTask).order_by(MaintenanceTask.due_date).all()
    return {"tasks": [_add_overdue(t) for t in tasks]}


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    task = MaintenanceTask(
        title=body.title, description=body.description,
        category=body.category, due_date=body.due_date,
        recurrence=body.recurrence,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _add_overdue(task)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, body: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if body.status is not None:
        task.status = body.status
    if body.due_date is not None:
        task.due_date = body.due_date
    db.commit()
    db.refresh(task)
    return _add_overdue(task)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
