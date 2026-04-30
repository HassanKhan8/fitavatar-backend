"""
database.py — SQLAlchemy Database Connection
Creates engine, session factory, and Base for all ORM models.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.config import DATABASE_URL

# Handle Render/Supabase postgres:// → postgresql:// URL fix
_db_url = DATABASE_URL
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

# Supabase Transaction Mode pooler (port 6543) requires NullPool
# because the pooler manages connections itself — SQLAlchemy must not pool
_use_null_pool = ":6543/" in _db_url

engine = create_engine(
    _db_url,
    poolclass=NullPool if _use_null_pool else None,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10, "sslmode": "require"},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yields DB session, always closes after request.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables if they don't exist. Called on app startup."""
    Base.metadata.create_all(bind=engine)
