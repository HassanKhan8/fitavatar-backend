"""
models/user.py — User table ORM model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id             = Column(Integer, primary_key=True, index=True)
    email          = Column(String, unique=True, index=True, nullable=False)
    supabase_uid   = Column(String, unique=True, index=True, nullable=False)
    name           = Column(String, nullable=False)
    age            = Column(Integer, nullable=False)
    weight_kg      = Column(Float, nullable=False)
    height_cm      = Column(Float, nullable=False)
    gender         = Column(String, nullable=False)          # "male" | "female"
    goal           = Column(String, nullable=False)          # "Weight Loss" | "Muscle Gain" | "Maintenance"
    activity_level = Column(String, nullable=False)          # "Sedentary" | "Lightly Active" | "Moderately Active" | "Very Active"
    country        = Column(String, nullable=False)
    created_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    workout_sessions = relationship("WorkoutSession", back_populates="user", cascade="all, delete")
    diet_logs          = relationship("DietLog",        back_populates="user", cascade="all, delete")
    user_progress_logs = relationship("UserProgress",      back_populates="user", cascade="all, delete")
