"""
routes/progress.py — Progress tracking endpoints
GET  /progress          → Full progress data (protected)
GET  /progress/weekly   → Weekly summaries only (protected)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.progress_service import get_full_progress, get_weekly_summaries

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("")
def get_progress(
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db),
):
    """
    Return complete progress data for the authenticated user:
    - All workout sessions (history)
    - Weekly summaries (last 8 weeks)
    - Complete physical user_progress history 
    - Diet plan history
    - Aggregate stats (total reps, avg score, total sessions)
    """
    return get_full_progress(user_id=current_user.id, db=db)


@router.get("/weekly")
def get_weekly(
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db),
    weeks:        int     = 8,
):
    """Return last N weeks of workout summaries."""
    return get_weekly_summaries(user_id=current_user.id, db=db, weeks=weeks)
