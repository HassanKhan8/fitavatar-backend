"""
schemas/session.py — Pydantic models for workout session requests/responses
"""

from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List


class SessionCreate(BaseModel):
    exercise_name:    str
    total_reps:       int
    correct_reps:     int
    incorrect_reps:   int
    score_percent:    float
    duration_seconds: int

    @field_validator("exercise_name")
    @classmethod
    def validate_exercise(cls, v):
        allowed = ["Squats", "Push-ups", "Bicep Curls"]
        if v not in allowed:
            raise ValueError(f"exercise must be one of: {allowed}")
        return v

    @field_validator("score_percent")
    @classmethod
    def validate_score(cls, v):
        if not (0.0 <= v <= 100.0):
            raise ValueError("score_percent must be 0–100")
        return round(v, 1)


class SessionResponse(BaseModel):
    id:               int
    user_id:          int
    exercise_name:    str
    total_reps:       int
    correct_reps:     int
    incorrect_reps:   int
    score_percent:    float
    duration_seconds: int
    recorded_at:      datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    total:    int
