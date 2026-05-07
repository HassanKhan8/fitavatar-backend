"""
routes/auth.py — Authentication & Profile setup endpoints
Because Supabase handles email/password login, this router only
handles creating the application-specific Profile linkage.

POST /auth/setup-profile — Link Supabase UUID to a new customized Profile
GET  /auth/me            — Get current user profile (protected)
PUT  /auth/profile       — Update user profile (protected)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app.database import get_db
from app.models.user import User
from app.models.user_progress import UserProgress
from app.schemas.auth import (
    ProfileSetupRequest, UserProfile, UpdateProfileRequest,
)
from app.services.auth_service import decode_token
from app.dependencies import get_current_user

bearer_scheme = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])


@router.post("/setup-profile", response_model=UserProfile, status_code=201)
def setup_profile(
    body: ProfileSetupRequest, 
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    """
    Called after Supabase signup. Requires the Supabase JWT.
    Creates the physical user profile in PostgreSQL.
    """
    token = credentials.credentials
    user_uuid = decode_token(token)

    if user_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Supabase token",
        )

    try:
        existing_by_uid = db.query(User).filter(User.supabase_uid == user_uuid).first()
        if existing_by_uid:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profile already set up for this Supabase account.",
            )

        existing_by_email = db.query(User).filter(User.email == body.email).first()
        if existing_by_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists in the profile database.",
            )

        user = User(
            email          = body.email,
            # Passwords are managed by Supabase Auth. We keep a non-sensitive placeholder
            # only to satisfy legacy NOT NULL DB schema during testing.
            password       = "__managed_by_supabase__",
            supabase_uid   = user_uuid,
            name           = body.name,
            age            = body.age,
            weight_kg      = body.weight_kg,
            height_cm      = body.height_cm,
            gender         = body.gender,
            goal           = body.goal,
            activity_level = body.activity_level,
            country        = body.country,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Log complete initial user progress
        progress_log = UserProgress(
            user_id   = user.id,
            age       = user.age,
            weight_kg = user.weight_kg,
            height_cm = user.height_cm,
            goal      = user.goal,
            location  = user.country,
        )
        db.add(progress_log)
        db.commit()

        return UserProfile.model_validate(user)

    except HTTPException:
        # Re-raise HTTP exceptions (409 Conflict, etc.)
        raise
    except OperationalError as e:
        db.rollback()
        error_msg = str(e)
        print(f"[ProfileSetup] Database error: {error_msg}")
        
        if "tenant/user" in error_msg or "ENOTFOUND" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection failed. Server misconfiguration: DATABASE_URL invalid or Supabase project unavailable. Admin should verify Render environment variables.",
            )
        elif "could not connect" in error_msg or "connection refused" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cannot connect to database server. Network or connectivity issue.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed. Please try again later.",
            )
    except Exception as e:
        db.rollback()
        print(f"[ProfileSetup] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error during profile setup.",
        )


@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user's profile."""
    return UserProfile.model_validate(current_user)


@router.put("/profile", response_model=UserProfile)
def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile fields and log a new UserProgress snapshot."""
    try:
        update_data = body.model_dump(exclude_unset=True)

        if not update_data:
            return UserProfile.model_validate(current_user)

        for field, value in update_data.items():
            setattr(current_user, field, value)

        # Log the complete snapshot after update
        progress_log = UserProgress(
            user_id   = current_user.id,
            age       = current_user.age,
            weight_kg = current_user.weight_kg,
            height_cm = current_user.height_cm,
            goal      = current_user.goal,
            location  = current_user.country,
        )
        db.add(progress_log)

        db.commit()
        db.refresh(current_user)
        return UserProfile.model_validate(current_user)

    except OperationalError as e:
        db.rollback()
        print(f"[ProfileUpdate] Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database operation failed. Please try again later.",
        )
    except Exception as e:
        db.rollback()
        print(f"[ProfileUpdate] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error during profile update.",
        )
