"""
main.py — FitAvatar FastAPI Application Entry Point
Registers all routers, CORS, startup events, and health check.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.config import APP_NAME, APP_VERSION
from app.database import create_tables, test_connection
from app.routes.auth import router as auth_router
from app.routes.diet import router as diet_router
from app.routes.sessions import router as sessions_router
from app.routes.progress import router as progress_router


# ── Lifespan: runs on startup and shutdown ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[{APP_NAME}] Starting up...")

    # Test database connection before proceeding
    try:
        test_connection()
        print(f"[{APP_NAME}] Database connection successful.")
    except RuntimeError as e:
        print(f"[{APP_NAME}] [CRITICAL] {str(e)}")
        print(f"[{APP_NAME}] Service startup FAILED - cannot proceed without database.")
        raise

    # Avoid unexpected DDL on managed databases in production.
    if os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true":
        try:
            create_tables()
            print(f"[{APP_NAME}] Database tables verified.")
        except Exception as e:
            print(f"[{APP_NAME}] [WARNING] Database warning: {e}")
            print(f"[{APP_NAME}]    Check DATABASE_URL env var in Render dashboard.")

    # Pre-load ML model so first request isn't slow
    try:
        from app.ml.diet_model import _load_model
        _load_model()
        print(f"[{APP_NAME}] ML model loaded.")
    except Exception as e:
        print(f"[{APP_NAME}] ML model load warning: {e}")

    yield
    # Shutdown
    print(f"[{APP_NAME}] Shutting down.")


# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title       = APP_NAME,
    version     = APP_VERSION,
    description = "AI-powered fitness assistant backend — pose evaluation + diet recommendation.",
    lifespan    = lifespan,
)

# ── CORS — allow Android app and any origin during development ────────────────
app.add_middleware(
    CORSMiddleware,
    # Android apps are not subject to browser CORS, but keeping this safe
    # prevents future web clients from failing with wildcard+credentials.
    allow_origins     = ["*"],   # Set explicit origins in production if you add a web frontend
    allow_credentials = False,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(diet_router)
app.include_router(sessions_router)
app.include_router(progress_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {
        "status":  "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"Welcome to {APP_NAME} v{APP_VERSION}",
        "docs":    "/docs",
        "health":  "/health",
    }
