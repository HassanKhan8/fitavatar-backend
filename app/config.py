"""
config.py — FitAvatar Backend Configuration
Loads all environment variables. Never hardcode secrets.

DATABASE_URL Format:
For Supabase (recommended for production):
  postgresql://postgres.PROJECT_ID:PASSWORD@aws-REGION.pooler.supabase.com:6543/postgres

  - PROJECT_ID: Your Supabase project ID (from dashboard)
  - PASSWORD: Database password (from Supabase settings)
  - REGION: AWS region (e.g., ap-south-1, us-east-1)
  - Port 6543 is the transaction-mode pooler (recommended)

  Example:
  postgresql://postgres.abcdefgh123456:mysecretpassword@aws-0-ap-south-1.pooler.supabase.com:6543/postgres

For local development:
  postgresql://postgres:password@localhost:5432/fitavatar
"""

from dotenv import load_dotenv
import os

load_dotenv()

# Detect managed runtimes (Render sets RENDER=true)
_IS_RENDER = os.getenv("RENDER", "").lower() == "true"

# ── Database ─────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/fitavatar"
)

# ── Supabase Auth ─────────────────────────────────────────────────────────────
SUPABASE_JWT_SECRET: str = os.getenv(
    "SUPABASE_JWT_SECRET",
    "missing-secret-key"
)

# Optional: allow multiple valid secrets during JWT secret rotation.
# Format: comma-separated list, e.g. "newsecret,oldsecret"
SUPABASE_JWT_SECRETS = [
    s.strip()
    for s in os.getenv("SUPABASE_JWT_SECRETS", "").split(",")
    if s.strip()
]

if (
    not SUPABASE_JWT_SECRETS
    and SUPABASE_JWT_SECRET
    and SUPABASE_JWT_SECRET != "missing-secret-key"
):
    SUPABASE_JWT_SECRETS = [SUPABASE_JWT_SECRET]

# ── App ───────────────────────────────────────────────────────────────────────
APP_NAME: str = "FitAvatar API"
APP_VERSION: str = "1.0.0"
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

# Fail-fast in production-like environments
# to avoid "works locally, breaks on Render".
if (_IS_RENDER or not DEBUG):

    if (
        not DATABASE_URL
        or "postgresql://postgres:password@localhost" in DATABASE_URL
    ):
        raise RuntimeError(
            "DATABASE_URL is not set correctly for production.\n"
            "Required format for Supabase:\n"
            "  postgresql://postgres.PROJECT_ID:PASSWORD@"
            "aws-REGION.pooler.supabase.com:6543/postgres\n"
            "Please check your Render environment variables dashboard."
        )

    if not SUPABASE_JWT_SECRETS:
        raise RuntimeError(
            "SUPABASE_JWT_SECRET (or SUPABASE_JWT_SECRETS) "
            "must be set in production."
        )

# ── ML Model Paths ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH: str = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "diet_recommender_weights.pth"
)

SCALER_PATH: str = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "nutrient_scaler.save"
)