"""
dashboard.py — Group Dashboard module router.
Milanote-style draggable cards with comments; persisted to dashboard.json.
"""
import json, os, uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException
from backend.schemas.dashboard import (
    CardCreate, CardUpdate, CommentCreate,
    CardResponse, CardsListResponse, CommentResponse
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "dashboard.json")


def _load() -> dict:
    try:
        with open(_DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"cards": []}


def _save(data: dict):
    with open(_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/cards", response_model=CardsListResponse)
def list_cards():
    return _load()


@router.post("/cards", response_model=CardResponse, status_code=201)
def create_card(body: CardCreate):
    data = _load()
    card = {
        "id": str(uuid.uuid4()),
        "title": body.title, "body": body.body,
        "color": body.color, "x": body.x, "y": body.y,
        "author": body.author, "comments": [],
        "created_at": _now(),
    }
    data["cards"].append(card)
    _save(data)
    return card


@router.patch("/cards/{card_id}", response_model=CardResponse)
def update_card(card_id: str, body: CardUpdate):
    data = _load()
    card = next((c for c in data["cards"] if c["id"] == card_id), None)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    for field, val in body.model_dump(exclude_none=True).items():
        card[field] = val
    _save(data)
    return card


@router.delete("/cards/{card_id}", status_code=204)
def delete_card(card_id: str):
    data = _load()
    card = next((c for c in data["cards"] if c["id"] == card_id), None)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    data["cards"] = [c for c in data["cards"] if c["id"] != card_id]
    _save(data)


@router.post("/cards/{card_id}/comments", response_model=CommentResponse, status_code=201)
def add_comment(card_id: str, body: CommentCreate):
    data = _load()
    card = next((c for c in data["cards"] if c["id"] == card_id), None)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    comment = {
        "id": str(uuid.uuid4()),
        "text": body.text, "author": body.author,
        "created_at": _now(),
    }
    card.setdefault("comments", []).append(comment)
    _save(data)
    return comment
