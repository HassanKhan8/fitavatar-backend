"""
models/session.py — WorkoutSession table ORM model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    exercise_name    = Column(String, nullable=False)     # "Squats" | "Push-ups" | "Bicep Curls"
    total_reps       = Column(Integer, nullable=False, default=0)
    correct_reps     = Column(Integer, nullable=False, default=0)
    incorrect_reps   = Column(Integer, nullable=False, default=0)
    score_percent    = Column(Float,   nullable=False, default=0.0)  # 0–100
    duration_seconds = Column(Integer, nullable=False, default=0)
    recorded_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="workout_sessions")
