from pydantic import BaseModel
from typing import Optional
from datetime import datetime

CARD_COLORS = ["#fffacd", "#d4f1f9", "#d5f5e3", "#fde8d8", "#e8daef"]


class CardCreate(BaseModel):
    title:  str
    body:   str = ""
    color:  str = "#fffacd"
    x:      float = 50.0
    y:      float = 50.0
    author: str = "anonymous"


class CardUpdate(BaseModel):
    title:  Optional[str] = None
    body:   Optional[str] = None
    color:  Optional[str] = None
    x:      Optional[float] = None
    y:      Optional[float] = None


class CommentCreate(BaseModel):
    text:   str
    author: str = "anonymous"


class CommentResponse(BaseModel):
    id:         str
    text:       str
    author:     str
    created_at: str


class CardResponse(BaseModel):
    id:         str
    title:      str
    body:       str
    color:      str
    x:          float
    y:          float
    author:     str
    comments:   list[CommentResponse] = []
    created_at: str


class CardsListResponse(BaseModel):
    cards: list[CardResponse]
