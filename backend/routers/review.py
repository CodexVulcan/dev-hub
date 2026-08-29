"""
review.py — Senior Review module router.
Priority-tags lines of change text (high/medium/low) using keyword rules.
"""
import json, re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.review import ReviewSummary
from backend.schemas.review import ReviewRequest, ReviewResponse, ReviewHistoryResponse

router = APIRouter(prefix="/api/review", tags=["review"])

_PRIORITY_RULES = [
    ("high",   ["security", "vulnerability", "cve", "breaking", "critical", "data loss", "breach", "exploit", "rce", "injection"]),
    ("medium", ["fix", "patch", "bug", "regression", "deprecated", "breaking change", "performance", "memory leak", "crash"]),
    ("low",    ["docs", "documentation", "style", "typo", "readme", "comment", "refactor", "cleanup", "whitespace", "rename"]),
]

_CATEGORY_RULES = [
    ("security",    ["security", "vulnerability", "cve", "auth", "token", "permission", "breach"]),
    ("bugfix",      ["fix", "bug", "patch", "regression", "crash", "error"]),
    ("performance", ["performance", "speed", "memory", "latency", "cache", "optimize"]),
    ("feature",     ["feat", "feature", "add", "new", "implement", "support"]),
    ("infra",       ["deploy", "ci", "cd", "docker", "kubernetes", "terraform", "pipeline"]),
    ("docs",        ["docs", "documentation", "readme", "changelog", "comment"]),
    ("style",       ["style", "format", "lint", "typo", "whitespace", "refactor", "rename"]),
]


def _classify_line(line: str) -> tuple[str, str]:
    lower = line.lower()
    priority = "low"
    for p, keywords in _PRIORITY_RULES:
        if any(kw in lower for kw in keywords):
            priority = p
            break
    category = "feature"
    for cat, keywords in _CATEGORY_RULES:
        if any(kw in lower for kw in keywords):
            category = cat
            break
    return priority, category


def _summarize(text: str) -> list[dict]:
    lines = [l.strip() for l in re.split(r"[\n;]", text) if l.strip() and len(l.strip()) > 3]
    items = []
    for line in lines:
        priority, category = _classify_line(line)
        summary = line[:120] + ("…" if len(line) > 120 else "")
        items.append({"summary": summary, "priority": priority, "category": category})
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(items, key=lambda x: order.get(x["priority"], 3))


@router.post("/summarize", response_model=ReviewResponse, status_code=201)
def summarize(body: ReviewRequest, db: Session = Depends(get_db)):
    if not body.changes_text.strip():
        raise HTTPException(status_code=422, detail="changes_text must not be empty")
    items = _summarize(body.changes_text)
    record = ReviewSummary(raw_input=body.changes_text, items_json=json.dumps(items))
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "items": items, "created_at": record.created_at}


@router.get("/history", response_model=ReviewHistoryResponse)
def list_history(db: Session = Depends(get_db)):
    records = db.query(ReviewSummary).order_by(ReviewSummary.created_at.desc()).all()
    history = []
    for r in records:
        history.append({
            "id": r.id,
            "items": json.loads(r.items_json),
            "created_at": r.created_at,
        })
    return {"history": history}
