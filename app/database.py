# """
# database.py — SQLAlchemy Database Connection
# Creates engine, session factory, and Base for all ORM models.
# """

# from sqlalchemy import create_engine, text
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool
# from sqlalchemy.exc import OperationalError
# from app.config import DATABASE_URL

# # Handle Render/Supabase postgres:// → postgresql:// URL fix
# _db_url = DATABASE_URL
# if _db_url.startswith("postgres://"):
#     _db_url = _db_url.replace("postgres://", "postgresql://", 1)

# # Supabase Transaction Mode pooler (port 6543) requires NullPool
# # because the pooler manages connections itself — SQLAlchemy must not pool
# _use_null_pool = ":6543/" in _db_url

# # Build connect_args based on connection type
# _connect_args = {"connect_timeout": 10}
# if _use_null_pool:
#     # Pooler connections work better without forcing SSL
#     _connect_args["sslmode"] = "prefer"
# else:
#     # Direct connections should enforce SSL
#     _connect_args["sslmode"] = "require"

# engine = create_engine(
#     _db_url,
#     poolclass=NullPool if _use_null_pool else None,
#     pool_pre_ping=True,
#     connect_args=_connect_args,
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


# def get_db():
#     """
#     FastAPI dependency — yields DB session, always closes after request.
#     Usage: db: Session = Depends(get_db)
    
#     Raises:
#         OperationalError: If database connection fails
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     except OperationalError as e:
#         db.close()
#         print(f"[DatabaseError] Connection failed: {str(e)}")
#         raise
#     finally:
#         db.close()


# def test_connection():
#     """
#     Test database connection on startup.
#     Raises RuntimeError if connection fails.
#     """
#     try:
#         with engine.connect() as conn:
#             result = conn.execute(text("SELECT 1"))
#             result.close()
#         return True
#     except OperationalError as e:
#         error_msg = str(e)
#         if "tenant/user" in error_msg or "ENOTFOUND" in error_msg:
#             raise RuntimeError(
#                 f"[DatabaseError] Supabase connection failed. Verify DATABASE_URL is correct. "
#                 f"Error: {error_msg}"
#             )
#         elif "could not connect" in error_msg or "connection refused" in error_msg:
#             raise RuntimeError(
#                 f"[DatabaseError] Could not connect to database server. "
#                 f"Check DATABASE_URL and network connectivity. Error: {error_msg}"
#             )
#         else:
#             raise RuntimeError(f"[DatabaseError] Connection test failed: {error_msg}")
#     except Exception as e:
#         raise RuntimeError(f"[DatabaseError] Unexpected error during connection test: {str(e)}")


# def create_tables():
#     """Create all tables if they don't exist. Called on app startup."""
#     try:
#         Base.metadata.create_all(bind=engine)
#     except OperationalError as e:
#         print(f"[DatabaseError] Failed to create tables: {str(e)}")

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
