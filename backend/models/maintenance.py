from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from backend.database import Base


class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    category = Column(String, nullable=False, default="other")
    due_date = Column(Date, nullable=False)
    recurrence = Column(String, nullable=False, default="none")  # none|weekly|monthly|quarterly
    status = Column(String, nullable=False, default="pending")   # pending | completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
