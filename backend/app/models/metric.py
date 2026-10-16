from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    step = Column(Integer, default=0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    run = relationship("Run", back_populates="metrics")
    
    __table_args__ = (
        Index("ix_metrics_run_name_step", "run_id", "name", "step"),
    )
