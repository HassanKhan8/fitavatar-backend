"""
models/diet_log.py — DietLog table ORM model
Stores each diet plan generated for a user.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class DietLog(Base):
    __tablename__ = "diet_logs"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    calories_target  = Column(Integer, nullable=False)
    protein_target   = Column(Integer, nullable=False)
    bmi_value        = Column(Float,   nullable=False)
    bmi_category     = Column(String,  nullable=False)
    goal             = Column(String,  nullable=False)
    location         = Column(String,  nullable=False)
    meals_json       = Column(JSON,    nullable=False)   # Full meal plan stored as JSON
    generated_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="diet_logs")
