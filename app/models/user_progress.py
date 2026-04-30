"""
models/user_progress.py — UserProgress table ORM model
Tracks user's physical profile changes over time.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    age       = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    goal      = Column(String, nullable=False)
    location  = Column(String, nullable=False)
    
    logged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="user_progress_logs")
