"""Test script to verify app configuration and imports"""
import sys
import os
sys.path.append(os.getcwd())

print("=" * 50)
print("TEST 1: Configuration & Imports")
print("=" * 50)

try:
    from app.config import DATABASE_URL, SUPABASE_JWT_SECRET, APP_NAME, APP_VERSION
    print(f"[OK] APP_NAME: {APP_NAME}")
    print(f"[OK] APP_VERSION: {APP_VERSION}")
    print(f"[OK] DATABASE_URL: {DATABASE_URL[:50]}...")
    if SUPABASE_JWT_SECRET == "missing-secret-key":
        print("[WARN] SUPABASE_JWT_SECRET not set!")
    else:
        print(f"[OK] SUPABASE_JWT_SECRET: {SUPABASE_JWT_SECRET[:15]}...")
except Exception as e:
    print(f"[FAIL] Config import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("TEST 2: Database Engine")
print("=" * 50)

try:
    from app.database import engine, get_db, create_tables
    print(f"[OK] Database engine created")
    print(f"[OK] Engine: {engine}")
except Exception as e:
    print(f"[FAIL] Database engine error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("TEST 3: FastAPI App")
print("=" * 50)

try:
    from app.main import app
    print(f"[OK] FastAPI app: {app.title}")
    # List all routes
    for route in app.routes:
        print(f"  - {route.methods} {route.path}")
except Exception as e:
    print(f"[FAIL] FastAPI app error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("TEST 4: Database Connection")
print("=" * 50)

try:
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"[OK] Database connection OK! Result: {result.scalar()}")
except Exception as e:
    print(f"[FAIL] Database connection error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("TEST 5: ML Model")
print("=" * 50)

try:
    from app.ml.diet_model import _load_model, compute_targets
    _load_model()
    print("[OK] ML model loaded")
    
    # Test compute_targets
    targets = compute_targets(weight=80, height=180, age=30, gender="male", goal="Muscle Gain")
    print(f"[OK] Compute targets: {targets}")
except Exception as e:
    print(f"[FAIL] ML model error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("TEST 6: BMI Calculation")
print("=" * 50)

try:
    from app.ml.bmi import bmi_profile
    bmi = bmi_profile(weight=80, height=180)
    print(f"[OK] BMI result: {bmi}")
except Exception as e:
    print(f"[FAIL] BMI error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("ALL TESTS COMPLETED")
print("=" * 50)
