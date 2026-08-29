from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class PipelineProject(Base):
    __tablename__ = "pipeline_projects"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False, unique=True)
    description  = Column(String, default="")
    github_owner = Column(String, nullable=True)
    github_repo  = Column(String, nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())


class PipelineStage(Base):
    __tablename__ = "pipeline_stages"

    id         = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pipeline_projects.id", ondelete="CASCADE"), nullable=False)
    stage      = Column(String, nullable=False)   # build | test | deploy
    status     = Column(String, nullable=False, default="pending")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
