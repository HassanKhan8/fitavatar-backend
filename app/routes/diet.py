"""
routes/diet.py — Diet recommendation endpoints
POST /diet/plan  → Generate & save personalised meal plan (protected)
GET  /diet/latest → Fetch latest saved diet plan (protected)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.diet_log import DietLog
from app.services.diet_service import get_diet_plan

router = APIRouter(prefix="/diet", tags=["Diet"])


@router.post("/plan")
def generate_plan(
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db),
):
    """
    Generate a personalised diet plan using the user's saved profile.
    Uses PyTorch DietNet model + country-specific food database.
    Saves result to diet_logs and returns complete plan.
    """
    try:
        plan = get_diet_plan(user=current_user, db=db)
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diet plan generation failed: {str(e)}",
        )


@router.get("/latest")
def get_latest_plan(
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db),
):
    """
    Return the most recently generated diet plan for this user.
    Returns 404 if no plan has been generated yet.
    """
    log = db.query(DietLog).filter(
        DietLog.user_id == current_user.id
    ).order_by(DietLog.generated_at.desc()).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No diet plan found. Generate one first.",
        )

    return {
        "goal":         log.goal,
        "location":     log.location,
        "bmi_value":    log.bmi_value,
        "bmi_profile":  log.bmi_category,
        "daily_targets": {
            "calories": log.calories_target,
            "protein":  log.protein_target,
        },
        "meals":        log.meals_json,
        "generated_at": log.generated_at.isoformat(),
    }
