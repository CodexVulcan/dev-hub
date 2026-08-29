from pydantic import BaseModel
from typing import Literal, Optional

NODE_TYPE = Literal["module", "service", "database", "external", "component"]


class NodeCreate(BaseModel):
    id:    str
    label: str
    type:  NODE_TYPE = "component"
    x:     float = 100.0
    y:     float = 100.0


class EdgeCreate(BaseModel):
    source: str
    target: str
    label:  str = ""


class NodeResponse(BaseModel):
    id:    str
    label: str
    type:  str
    x:     float
    y:     float


class EdgeResponse(BaseModel):
    source: str
    target: str
    label:  str


class MindmapResponse(BaseModel):
    nodes: list[NodeResponse]
    edges: list[EdgeResponse]
