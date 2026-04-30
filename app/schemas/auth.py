"""
schemas/auth.py — Pydantic models for auth requests/responses
Because we use Supabase Auth, we only need a profile setup schema.
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

# Exact countries present in the training dataset CSV
SUPPORTED_COUNTRIES = [
    "Brazil", "China", "France", "Greece", "India", "Italy",
    "Japan", "Lebanon", "Mexico", "Pakistan", "Saudi Arabia",
    "Spain", "Thailand", "Turkey", "USA",
]


class ProfileSetupRequest(BaseModel):
    email:          EmailStr
    name:           str
    age:            int
    weight_kg:      float
    height_cm:      float
    gender:         str          # "male" | "female"
    goal:           str          # "Weight Loss" | "Muscle Gain" | "Maintenance"
    activity_level: str          # "Sedentary" | "Lightly Active" | "Moderately Active" | "Very Active"
    country:        str

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v.lower() not in ["male", "female"]:
            raise ValueError("gender must be 'male' or 'female'")
        return v.lower()

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, v):
        allowed = {
            "weight loss": "Weight Loss",
            "muscle gain": "Muscle Gain",
            "maintenance": "Maintenance",
        }
        result = allowed.get(v.strip().lower())
        if not result:
            raise ValueError("goal must be one of: Weight Loss, Muscle Gain, Maintenance")
        return result


    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if not (10 <= v <= 100):
            raise ValueError("age must be between 10 and 100")
        return v

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v):
        if not (20.0 <= v <= 300.0):
            raise ValueError("weight must be between 20 and 300 kg")
        return v

    @field_validator("height_cm")
    @classmethod
    def validate_height(cls, v):
        if not (100.0 <= v <= 250.0):
            raise ValueError("height must be between 100 and 250 cm")
        return v

    @field_validator("country")
    @classmethod
    def validate_country(cls, v):
        # Normalise to title-case then check against supported list
        title = v.strip().title()
        lower_map = {c.lower(): c for c in SUPPORTED_COUNTRIES}
        matched = lower_map.get(v.strip().lower())
        if not matched:
            raise ValueError(
                f"country must be one of the 15 supported countries: {SUPPORTED_COUNTRIES}"
            )
        return matched


from uuid import UUID

class UserProfile(BaseModel):
    id:             int
    supabase_uid:   str
    email:          str
    name:           str
    age:            int
    weight_kg:      float
    height_cm:      float
    gender:         str
    goal:           str
    activity_level: str
    country:        str

    @field_validator("supabase_uid", mode="before")
    @classmethod
    def transform_uuid(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    name:           Optional[str]   = None
    age:            Optional[int]   = None
    weight_kg:      Optional[float] = None
    height_cm:      Optional[float] = None
    goal:           Optional[str]   = None
    activity_level: Optional[str]   = None
    country:        Optional[str]   = None

    @field_validator("country", mode="before")
    @classmethod
    def validate_country(cls, v):
        if v is None:
            return v
        lower_map = {c.lower(): c for c in SUPPORTED_COUNTRIES}
        matched = lower_map.get(v.strip().lower())
        if not matched:
            raise ValueError(
                f"country must be one of: {SUPPORTED_COUNTRIES}"
            )
        return matched
