from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

PRIORITY = Literal["high", "medium", "low"]
CATEGORY = Literal["security", "feature", "bugfix", "performance", "docs", "style", "infra"]


class ReviewRequest(BaseModel):
    changes_text: str


class ReviewItem(BaseModel):
    summary:  str
    priority: str
    category: str


class ReviewResponse(BaseModel):
    id:         int
    items:      list[ReviewItem]
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReviewHistoryResponse(BaseModel):
    history: list[ReviewResponse]
