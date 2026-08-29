from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class DebuggingReport(Base):
    __tablename__ = "debugging_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DebuggingIssue(Base):
    __tablename__ = "debugging_issues"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("debugging_reports.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    severity = Column(String, nullable=False)   # critical | major | minor
    suggested_fix = Column(String, default="")
    status = Column(String, nullable=False, default="open")  # open | resolved
