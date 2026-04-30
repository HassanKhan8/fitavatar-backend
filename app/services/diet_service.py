"""
services/diet_service.py
Orchestrates full diet recommendation pipeline:
  1. Mifflin-St Jeor BMR + goal adjustment → calorie & protein targets
  2. BMI calculation
  3. AI-ranked country-specific meal plan (DietTensorModel)
  4. Persist to diet_logs
"""
from sqlalchemy.orm import Session
from app.ml.bmi import bmi_profile
from app.ml.diet_model import compute_targets
from app.ml.diet_generator import generate_meal_plan
from app.models.diet_log import DietLog
from app.models.user import User


def get_diet_plan(user: User, db: Session) -> dict:
    """Generate and persist a full diet plan for the user."""

    # 1. BMI
    bmi_info = bmi_profile(user.weight_kg, user.height_cm)

    # 2. Calorie + protein targets (Mifflin-St Jeor, matches notebook)
    targets = compute_targets(
        weight = user.weight_kg,
        height = user.height_cm,
        age    = user.age,
        gender = user.gender,
        goal   = user.goal,
    )

    # 3. AI-ranked country meal plan
    meals = generate_meal_plan(
        location        = user.country,
        target_calories = targets["calories"],
        target_protein  = targets["protein"],
        user_id         = user.id,
    )

    # 4. Persist
    diet_log = DietLog(
        user_id         = user.id,
        calories_target = targets["calories"],
        protein_target  = targets["protein"],
        bmi_value       = bmi_info["bmi"],
        bmi_category    = bmi_info["category"],
        goal            = user.goal,
        location        = user.country,
        meals_json      = meals,
    )
    db.add(diet_log)
    db.commit()
    db.refresh(diet_log)

    return {
        "goal":         user.goal,
        "location":     user.country.title(),
        "bmi_value":    bmi_info["bmi"],
        "bmi_profile":  bmi_info["category"],
        "bmi_advice":   bmi_info["advice"],
        "daily_targets": {
            "calories": targets["calories"],
            "protein":  targets["protein"],
        },
        "meals":        meals,
        "generated_at": diet_log.generated_at.isoformat(),
    }
