from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from backend.database import Base


class ReviewSummary(Base):
    __tablename__ = "review_summaries"

    id = Column(Integer, primary_key=True, index=True)
    raw_input = Column(Text, nullable=False)
    items_json = Column(Text, nullable=False)   # JSON-serialised list of priority items
    created_at = Column(DateTime(timezone=True), server_default=func.now())
