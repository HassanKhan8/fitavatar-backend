"""Debug script to test database connectivity"""
import sys
import os
sys.path.append(os.getcwd())

print("[DEBUG] Testing database connection...")

# Test 1: Import app config
print("[DEBUG] Step 1: Checking config...")
from app.config import DATABASE_URL
print(f"[DEBUG] DATABASE_URL: {DATABASE_URL[:50]}...")

# Test 2: Import and setup database
print("[DEBUG] Step 2: Setting up database engine...")
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

_db_url = DATABASE_URL
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

_use_null_pool = ":6543/" in _db_url
print(f"[DEBUG] Using NullPool: {_use_null_pool}")

engine = create_engine(
    _db_url,
    poolclass=NullPool if _use_null_pool else None,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10, "sslmode": "require"},
)

print("[DEBUG] Step 3: Testing connection...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"[DEBUG] Connection OK! Result: {result.scalar()}")
except Exception as e:
    print(f"[DEBUG] Connection FAILED: {e}")
    import traceback
    traceback.print_exc()
