"""
routes/sessions.py — Workout session endpoints
POST /sessions          → Save a completed workout session (protected)
GET  /sessions          → Get all sessions for current user (protected)
GET  /sessions/{id}     → Get a specific session (protected)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.session import WorkoutSession
from app.schemas.session import SessionCreate, SessionResponse, SessionListResponse

router = APIRouter(prefix="/sessions", tags=["Workout Sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
def save_session(
    body:         SessionCreate,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db),
):
    """Save a completed workout session after the user finishes exercising."""
    session = WorkoutSession(
        user_id          = current_user.id,
        exercise_name    = body.exercise_name,
        total_reps       = body.total_reps,
        correct_reps     = body.correct_reps,
        incorrect_reps   = body.incorrect_reps,
        score_percent    = body.score_percent,
        duration_seconds = body.duration_seconds,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("", response_model=SessionListResponse)
def get_my_sessions(
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db),
    limit:        int     = 50,
    offset:       int     = 0,
):
    """Get all workout sessions for the authenticated user, newest first."""
    sessions = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == current_user.id
    ).order_by(WorkoutSession.recorded_at.desc()).offset(offset).limit(limit).all()

    total = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == current_user.id
    ).count()

    return SessionListResponse(sessions=sessions, total=total)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id:   int,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db),
):
    """Get a specific workout session by ID."""
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id      == session_id,
        WorkoutSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    return session
