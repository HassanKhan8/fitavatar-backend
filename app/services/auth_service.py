"""
services/auth_service.py — Authentication business logic
For Supabase Auth, we only need to decode and verify the JWT token
provided by the client using our SUPABASE_JWT_SECRET.
"""

from jose import JWTError, jwt
from typing import Optional
from app.config import SUPABASE_JWT_SECRETS

# Supabase Auth tokens use HS256 by default
ALGORITHM = "HS256"

def decode_token(token: str) -> Optional[str]:
    """
    Decode Supabase JWT and return the user UUID.
    Returns None if token is invalid or expired.
    """
    if not token or token == "undefined":
        return None

    last_error: Optional[Exception] = None
    for secret in SUPABASE_JWT_SECRETS:
        try:
            # Supabase access tokens are signed with the project JWT secret (HS256)
            payload = jwt.decode(
                token,
                secret,
                algorithms=[ALGORITHM],
                options={
                    "verify_aud": False,  # Common in multi-project setups
                    "verify_exp": True,   # Ensure we catch expired tokens
                },
            )
            user_uuid = payload.get("sub")
            return str(user_uuid) if user_uuid else None
        except JWTError as e:
            last_error = e
            continue

    # Safe diagnostics: never print the raw token. Unverified claims are only used for logging hints.
    try:
        claims = jwt.get_unverified_claims(token)
        role = claims.get("role")
        ref = claims.get("ref") or claims.get("project_ref")
        aud = claims.get("aud")
        exp = claims.get("exp")
        print(
            "[AuthService] Token decode failed; hints="
            f"role={role!r} ref={ref!r} aud={aud!r} exp={exp!r} err={last_error}"
        )
    except Exception:
        print(f"[AuthService] Token decode failed: {last_error}")

    return None
