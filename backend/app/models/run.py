from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class RunStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Run(Base):
    __tablename__ = "runs"
    
    id = Column(String, primary_key=True)  # UUID
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String)
    status = Column(Enum(RunStatus), default=RunStatus.RUNNING, nullable=False, index=True)
    params = Column(JSON, default={})
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    source_commit = Column(String)
    dataset_name = Column(String)
    dataset_version = Column(String)
    error_message = Column(String)
    
    experiment = relationship("Experiment", back_populates="runs")
    metrics = relationship("Metric", back_populates="run", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="run", cascade="all, delete-orphan")
