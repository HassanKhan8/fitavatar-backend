"""
schemas/diet.py — Pydantic models for diet plan requests/responses
"""

from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional


class FoodItem(BaseModel):
    name:     str
    protein:  int
    calories: int


class MealOption(BaseModel):
    option: int
    foods:  List[FoodItem]


class DailyTargets(BaseModel):
    calories: int
    protein:  int


class DietResponse(BaseModel):
    goal:           str
    location:       str
    bmi_value:      float
    bmi_profile:    str
    daily_targets:  DailyTargets
    meals:          Dict[str, List[Dict[str, Any]]]
    generated_at:   Optional[datetime] = None

    class Config:
        from_attributes = True


class DietLogResponse(BaseModel):
    id:              int
    calories_target: int
    protein_target:  int
    bmi_value:       float
    bmi_category:    str
    goal:            str
    location:        str
    meals_json:      Dict[str, Any]
    generated_at:    datetime

    class Config:
        from_attributes = True
