"""
config.py — FitAvatar Backend Configuration
Loads all environment variables. Never hardcode secrets.
"""

from dotenv import load_dotenv
import os

load_dotenv()

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

# ── App ───────────────────────────────────────────────────────────────────────
APP_NAME: str = "FitAvatar API"
APP_VERSION: str = "1.0.0"
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

# ── ML Model Paths ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH: str = os.path.join(BASE_DIR, "ml", "models", "diet_recommender_weights.pth")
SCALER_PATH: str = os.path.join(BASE_DIR, "ml", "models", "nutrient_scaler.save")
