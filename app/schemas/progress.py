"""
schemas/progress.py — Pydantic models for progress tracking
"""

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict


class UserProgressResponse(BaseModel):
    id:        int
    age:       int
    weight_kg: float
    height_cm: float
    goal:      str
    location:  str
    logged_at: datetime

    class Config:
        from_attributes = True


class WeeklySummary(BaseModel):
    week_label:         str        # e.g. "Mar 18 – Mar 24"
    total_sessions:     int
    total_reps:         int
    avg_score_percent:  float
    best_exercise:      Optional[str]
    calories_target:    Optional[int]


class ProgressResponse(BaseModel):
    workout_history: List[Dict]
    weekly_summary:  List[WeeklySummary]
    user_progress:   List[UserProgressResponse]
    diet_history:    List[Dict]
    total_sessions:  int
    total_reps:      int
    avg_score:       float
