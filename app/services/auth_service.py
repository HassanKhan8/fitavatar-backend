"""
services/auth_service.py — Authentication business logic
Supports both legacy HS256 (shared JWT secret) and modern
asymmetric Supabase JWTs (RS256/ES256 via JWKS).
"""

import time
from typing import Optional

import httpx
from jose import JWTError, jwt
from app.config import SUPABASE_JWT_SECRETS

_JWKS_CACHE: dict[str, dict] = {}
_JWKS_FETCHED_AT: dict[str, float] = {}
_JWKS_TTL_SECONDS = 3600


def _resolve_jwks_url(token: str) -> Optional[str]:
    """
    Build Supabase JWKS URL from token issuer claim.
    Supabase issuer usually looks like: https://<ref>.supabase.co/auth/v1
    """
    try:
        claims = jwt.get_unverified_claims(token)
        issuer = str(claims.get("iss") or "").strip()
        if not issuer:
            return None
        return issuer.rstrip("/") + "/.well-known/jwks.json"
    except Exception:
        return None


def _get_jwks(jwks_url: str) -> Optional[dict]:
    now = time.time()
    cached = _JWKS_CACHE.get(jwks_url)
    fetched_at = _JWKS_FETCHED_AT.get(jwks_url, 0)
    if cached and (now - fetched_at) < _JWKS_TTL_SECONDS:
        return cached

    try:
        with httpx.Client(timeout=8.0) as client:
            res = client.get(jwks_url)
            res.raise_for_status()
            jwks = res.json()
        if isinstance(jwks, dict) and isinstance(jwks.get("keys"), list):
            _JWKS_CACHE[jwks_url] = jwks
            _JWKS_FETCHED_AT[jwks_url] = now
            return jwks
    except Exception as e:
        print(f"[AuthService] JWKS fetch failed: {e}")

    return None

def decode_token(token: str) -> Optional[str]:
    """
    Decode Supabase JWT and return the user UUID.
    Returns None if token is invalid or expired.
    """
    if not token or token == "undefined":
        return None

    try:
        header = jwt.get_unverified_header(token)
    except Exception as e:
        print(f"[AuthService] Token header parse failed: {e}")
        return None

    alg = str(header.get("alg") or "")
    kid = header.get("kid")
    last_error: Optional[Exception] = None

    if alg.startswith("HS"):
        for secret in SUPABASE_JWT_SECRETS:
            try:
                payload = jwt.decode(
                    token,
                    secret,
                    algorithms=[alg],
                    options={
                        "verify_aud": False,
                        "verify_exp": True,
                    },
                )
                user_uuid = payload.get("sub")
                return str(user_uuid) if user_uuid else None
            except JWTError as e:
                last_error = e
                continue
    elif alg.startswith("RS") or alg.startswith("ES"):
        jwks_url = _resolve_jwks_url(token)
        jwks = _get_jwks(jwks_url) if jwks_url else None
        keys = (jwks or {}).get("keys", [])

        for key in keys:
            if kid and key.get("kid") != kid:
                continue
            try:
                payload = jwt.decode(
                    token,
                    key,
                    algorithms=[alg],
                    options={
                        "verify_aud": False,
                        "verify_exp": True,
                    },
                )
                user_uuid = payload.get("sub")
                return str(user_uuid) if user_uuid else None
            except JWTError as e:
                last_error = e
                continue
    else:
        last_error = JWTError(f"Unsupported token algorithm: {alg!r}")

    # Safe diagnostics: never print the raw token. Unverified claims are only used for logging hints.
    try:
        claims = jwt.get_unverified_claims(token)
        role = claims.get("role")
        ref = claims.get("ref") or claims.get("project_ref")
        aud = claims.get("aud")
        exp = claims.get("exp")
        print(
            "[AuthService] Token decode failed; hints="
            f"alg={alg!r} kid={kid!r} role={role!r} ref={ref!r} aud={aud!r} exp={exp!r} err={last_error}"
        )
    except Exception:
        print(f"[AuthService] Token decode failed: {last_error}")

    return None
