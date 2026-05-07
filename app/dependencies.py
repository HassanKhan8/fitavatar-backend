"""
dependencies.py — FastAPI dependencies
Provides get_current_user dependency for all protected routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app.database import get_db
from app.services.auth_service import decode_token
from app.models.user import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extracts and validates JWT from Authorization header.
    Returns the authenticated User ORM object via supabase_uid.
    Raises 401 if token is missing, invalid, or expired.
    Raises 503 if database connection fails.
    """
    token = credentials.credentials
    user_uuid = decode_token(token)

    if user_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Supabase token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = db.query(User).filter(User.supabase_uid == user_uuid).first()
        if user is None:
            # If the user exists in Supabase Auth but not in our 'users' Postgres table
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found. Please complete the setup profile step.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    except OperationalError as e:
        print(f"[CurrentUser] Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed. Please try again later.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[CurrentUser] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during authentication.",
            headers={"WWW-Authenticate": "Bearer"},
        )
