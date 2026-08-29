"""
mindmap.py -- Project Mindmap module router.
Persists graph to backend/data/mindmap.json.
"""
import json, os
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.schemas.mindmap import (
    NodeCreate, EdgeCreate, MindmapResponse, NodeResponse, EdgeResponse
)

router = APIRouter(prefix="/api/mindmap", tags=["mindmap"])
_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "mindmap.json")

def _load() -> dict:
    try:
        with open(_DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"nodes": [], "edges": []}

def _save(data: dict):
    with open(_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@router.get("", response_model=MindmapResponse)
def get_mindmap():
    return _load()

@router.post("/nodes", response_model=NodeResponse, status_code=201)
def add_node(body: NodeCreate):
    data = _load()
    if any(n["id"] == body.id for n in data["nodes"]):
        raise HTTPException(status_code=409, detail="Node ID already exists")
    node = body.model_dump()
    data["nodes"].append(node)
    _save(data)
    return node

@router.post("/edges", response_model=EdgeResponse, status_code=201)
def add_edge(body: EdgeCreate):
    data = _load()
    node_ids = {n["id"] for n in data["nodes"]}
    if body.source not in node_ids:
        raise HTTPException(status_code=404, detail="Source node not found")
    if body.target not in node_ids:
        raise HTTPException(status_code=404, detail="Target node not found")
    edge = body.model_dump()
    data["edges"].append(edge)
    _save(data)
    return edge

@router.patch("/nodes/{node_id}", response_model=NodeResponse)
def update_node_position(
    node_id: str,
    x: Optional[float] = Query(None),
    y: Optional[float] = Query(None),
    label: Optional[str] = Query(None),
):
    """Update node x/y position or label via query params."""
    data = _load()
    node = next((n for n in data["nodes"] if n["id"] == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    if x is not None:
        node["x"] = x
    if y is not None:
        node["y"] = y
    if label is not None:
        node["label"] = label
    _save(data)
    return node

@router.delete("/nodes/{node_id}", status_code=204)
def delete_node(node_id: str):
    data = _load()
    if not any(n["id"] == node_id for n in data["nodes"]):
        raise HTTPException(status_code=404, detail="Node not found")
    data["nodes"] = [n for n in data["nodes"] if n["id"] != node_id]
    data["edges"] = [e for e in data["edges"] if e["source"] != node_id and e["target"] != node_id]
    _save(data)
    return None