"""
services/progress_service.py
Aggregates workout sessions and diet logs into
weekly summaries and progress stats.
"""

from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.session import WorkoutSession
from app.models.diet_log import DietLog
from app.models.user_progress import UserProgress


def get_weekly_summaries(user_id: int, db: Session, weeks: int = 8) -> List[dict]:
    """
    Return last `weeks` weeks of workout summaries.
    Each week: label, total_sessions, total_reps, avg_score, best_exercise.
    """
    summaries = []
    now = datetime.now(timezone.utc)

    for i in range(weeks - 1, -1, -1):
        week_end   = now - timedelta(weeks=i)
        week_start = week_end - timedelta(weeks=1)

        sessions = db.query(WorkoutSession).filter(
            WorkoutSession.user_id    == user_id,
            WorkoutSession.recorded_at >= week_start,
            WorkoutSession.recorded_at <  week_end,
        ).all()

        if not sessions:
            label = _week_label(week_start, week_end)
            summaries.append({
                "week_label":        label,
                "total_sessions":    0,
                "total_reps":        0,
                "avg_score_percent": 0.0,
                "best_exercise":     None,
                "calories_target":   None,
            })
            continue

        total_reps  = sum(s.total_reps for s in sessions)
        avg_score   = round(sum(s.score_percent for s in sessions) / len(sessions), 1)

        # Best exercise = most reps
        exercise_reps: dict = {}
        for s in sessions:
            exercise_reps[s.exercise_name] = exercise_reps.get(s.exercise_name, 0) + s.total_reps
        best_exercise = max(exercise_reps, key=exercise_reps.get) if exercise_reps else None

        # Latest diet calorie target this week
        diet_log = db.query(DietLog).filter(
            DietLog.user_id      == user_id,
            DietLog.generated_at >= week_start,
            DietLog.generated_at <  week_end,
        ).order_by(DietLog.generated_at.desc()).first()

        summaries.append({
            "week_label":        _week_label(week_start, week_end),
            "total_sessions":    len(sessions),
            "total_reps":        total_reps,
            "avg_score_percent": avg_score,
            "best_exercise":     best_exercise,
            "calories_target":   diet_log.calories_target if diet_log else None,
        })

    return summaries


def _week_label(start: datetime, end: datetime) -> str:
    return f"{start.strftime('%b %d')} – {end.strftime('%b %d')}"


def get_full_progress(user_id: int, db: Session) -> dict:
    """Return complete progress data for a user."""

    # All sessions — newest first
    sessions = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == user_id
    ).order_by(WorkoutSession.recorded_at.desc()).all()

    # All diet logs — newest first
    diet_logs = db.query(DietLog).filter(
        DietLog.user_id == user_id
    ).order_by(DietLog.generated_at.desc()).all()

    # All user progress logs — oldest first (for chart)
    progress_logs = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).order_by(UserProgress.logged_at.asc()).all()

    # Aggregates
    total_reps = sum(s.total_reps for s in sessions)
    avg_score  = round(
        sum(s.score_percent for s in sessions) / len(sessions), 1
    ) if sessions else 0.0

    return {
        "workout_history": [_session_to_dict(s) for s in sessions],
        "weekly_summary":  get_weekly_summaries(user_id, db),
        "user_progress":   [_progress_to_dict(w) for w in progress_logs],
        "diet_history":    [_diet_to_dict(d) for d in diet_logs],
        "total_sessions":  len(sessions),
        "total_reps":      total_reps,
        "avg_score":       avg_score,
    }


def _session_to_dict(s: WorkoutSession) -> dict:
    return {
        "id":               s.id,
        "exercise_name":    s.exercise_name,
        "total_reps":       s.total_reps,
        "correct_reps":     s.correct_reps,
        "incorrect_reps":   s.incorrect_reps,
        "score_percent":    s.score_percent,
        "duration_seconds": s.duration_seconds,
        "recorded_at":      s.recorded_at.isoformat(),
    }


def _progress_to_dict(p: UserProgress) -> dict:
    return {
        "id":        p.id,
        "age":       p.age,
        "weight_kg": p.weight_kg,
        "height_cm": p.height_cm,
        "goal":      p.goal,
        "location":  p.location,
        "logged_at": p.logged_at.isoformat(),
    }


def _diet_to_dict(d: DietLog) -> dict:
    return {
        "id":               d.id,
        "calories_target":  d.calories_target,
        "protein_target":   d.protein_target,
        "bmi_value":        d.bmi_value,
        "bmi_category":     d.bmi_category,
        "goal":             d.goal,
        "location":         d.location,
        "meals_json":       d.meals_json,
        "generated_at":     d.generated_at.isoformat(),
    }
