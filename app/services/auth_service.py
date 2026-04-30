"""
services/auth_service.py — Authentication business logic
For Supabase Auth, we only need to decode and verify the JWT token
provided by the client using our SUPABASE_JWT_SECRET.
"""

from jose import JWTError, jwt
from typing import Optional
from app.config import SUPABASE_JWT_SECRET

# Supabase Auth tokens use HS256 by default
ALGORITHM = "HS256"

def decode_token(token: str) -> Optional[str]:
    """
    Decode Supabase JWT and return the user UUID.
    Returns None if token is invalid or expired.
    """
    if not token or token == "undefined":
        return None

    try:
        # Supabase tokens are signed with the project JWT secret
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=[ALGORITHM],
            options={
                "verify_aud": False,  # Common in multi-project setups
                "verify_exp": True    # Ensure we catch expired tokens
            }
        )
        user_uuid = payload.get("sub")
        return str(user_uuid) if user_uuid else None
    except JWTError as e:
        print(f"[AuthService] Token decode failed: {str(e)}")
        return None
