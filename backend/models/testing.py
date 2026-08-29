from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    test_suite = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False)
    test_name = Column(String, nullable=False)
    status = Column(String, nullable=False)       # passed | failed | skipped | error
    message = Column(String, default="")
    severity = Column(String, nullable=False, default="info")  # critical | warning | info
