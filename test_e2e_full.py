"""
FitAvatar Backend - Comprehensive End-to-End API Test Suite
Tests all endpoints in a logical user journey flow.
"""

import sys
import os
import uuid
import json
from datetime import datetime
from typing import Dict, Any

# Add current directory to path
sys.path.append(os.getcwd())

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal, engine, get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.diet_log import DietLog
from app.models.session import WorkoutSession
from app.models.user_progress import UserProgress

# --- CONFIGURATION & MOCKS ---

TEST_USER_EMAIL = f"e2e_test_{uuid.uuid4().hex[:8]}@example.com"
TEST_SUPABASE_UID = str(uuid.uuid4())
MOCK_TOKEN = "mock-e2e-token"

# This will hold the user object once created
test_user_instance = None

def mock_get_current_user(db: Session = Depends(get_db)):
    """Mock dependency that always returns the test user from the current DB session."""
    user = db.query(User).filter(User.supabase_uid == TEST_SUPABASE_UID).first()
    return user

# For setup-profile which calls decode_token directly
import app.routes.auth as auth_routes
from unittest.mock import patch

# --- TEST CLIENT SETUP ---

client = TestClient(app)

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def print_header(title):
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}STEP: {title}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

def print_result(name, passed, details=""):
    status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    print(f"[{status}] {name}")
    if details:
        print(f"      {details}")

# --- GLOBAL STATE ---
state = {
    "user_id": None,
    "diet_log_id": None,
    "session_id": None
}

# --- TESTS ---

def test_01_setup_profile():
    print_header("1. Setup Profile (POST /auth/setup-profile)")
    
    payload = {
        "email": TEST_USER_EMAIL,
        "name": "E2E Test User",
        "age": 28,
        "weight_kg": 75.5,
        "height_cm": 178.0,
        "gender": "male",
        "goal": "Muscle Gain",
        "activity_level": "Moderately Active",
        "country": "Pakistan"
    }
    
    # We need to mock decode_token in the auth routes module
    with patch("app.routes.auth.decode_token", return_value=TEST_SUPABASE_UID):
        response = client.post(
            "/auth/setup-profile",
            json=payload,
            headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
        )
    
    passed = response.status_code == 201
    data = response.json()
    
    if passed:
        state["user_id"] = data["id"]
        # Update global test_user_instance for the mock dependency
        db = SessionLocal()
        global test_user_instance
        test_user_instance = db.query(User).filter(User.id == data["id"]).first()
        db.close()
        
    print_result("Profile Setup", passed, f"Status: {response.status_code}, User ID: {state['user_id']}")
    return passed

def test_02_get_me():
    print_header("2. Get Current User (GET /auth/me)")
    
    # Override the dependency for protected routes
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )
    
    data = response.json()
    passed = response.status_code == 200 and data["email"] == TEST_USER_EMAIL
    
    print_result("Get Me", passed, f"Status: {response.status_code}, Email: {data.get('email')}")
    return passed

def test_03_update_profile():
    print_header("3. Update Profile (PUT /auth/profile)")
    
    payload = {
        "weight_kg": 76.5,
        "goal": "Maintenance"
    }
    
    response = client.put(
        "/auth/profile",
        json=payload,
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )
    
    data = response.json()
    passed = response.status_code == 200 and data["weight_kg"] == 76.5 and data["goal"] == "Maintenance"
    
    print_result("Update Profile", passed, f"Status: {response.status_code}, New Weight: {data.get('weight_kg')}")
    return passed

def test_04_generate_diet():
    print_header("4. Generate Diet Plan (POST /diet/plan)")
    
    response = client.post(
        "/diet/plan",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )
    
    data = response.json()
    # Check if BMI and targets are present
    passed = response.status_code == 200 and "bmi_value" in data and "daily_targets" in data
    
    print_result("Generate Diet", passed, f"Status: {response.status_code}, BMI: {data.get('bmi_value')}")
    return passed

def test_05_get_latest_diet():
    print_header("5. Get Latest Diet (GET /diet/latest)")
    
    response = client.get(
        "/diet/latest",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )
    
    data = response.json()
    passed = response.status_code == 200 and "meals" in data
    
    print_result("Get Latest Diet", passed, f"Status: {response.status_code}, Meals: {list(data.get('meals', {}).keys())}")
    return passed

def test_06_record_session():
    print_header("6. Record Exercise Session (POST /sessions)")
    
    payload = {
        "exercise_name": "Squats",
        "total_reps": 15,
        "correct_reps": 12,
        "incorrect_reps": 3,
        "score_percent": 80.0,
        "duration_seconds": 90
    }
    
    response = client.post(
        "/sessions",
        json=payload,
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )
    
    data = response.json()
    passed = response.status_code == 201
    
    if passed:
        state["session_id"] = data["id"]
        
    print_result("Record Session", passed, f"Status: {response.status_code}, Session ID: {state['session_id']}")
    return passed

def test_07_get_sessions():
    print_header("7. Get Session History (GET /sessions)")
    
    response = client.get(
        "/sessions",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )
    
    data = response.json()
    passed = response.status_code == 200 and len(data.get("sessions", [])) >= 1
    
    print_result("Get Sessions", passed, f"Status: {response.status_code}, Total: {data.get('total')}")
    return passed

def test_08_get_progress():
    print_header("8. Get Progress Analytics (GET /progress)")
    
    response = client.get(
        "/progress",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )
    
    data = response.json()
    # Actual API returns flat stats: total_reps, total_sessions, avg_score
    passed = response.status_code == 200 and "total_reps" in data and "total_sessions" in data
    
    if passed:
        print(f"      Stats: Total Reps={data.get('total_reps')}, Total Sessions={data.get('total_sessions')}, Avg Score={data.get('avg_score')}%")
        
    print_result("Get Progress", passed, f"Status: {response.status_code}")
    return passed

# --- CLEANUP ---

def cleanup():
    print_header("CLEANUP")
    db = SessionLocal()
    try:
        if state["user_id"]:
            # Delete associated records first due to FK constraints
            db.query(WorkoutSession).filter(WorkoutSession.user_id == state["user_id"]).delete()
            db.query(DietLog).filter(DietLog.user_id == state["user_id"]).delete()
            db.query(UserProgress).filter(UserProgress.user_id == state["user_id"]).delete()
            db.query(User).filter(User.id == state["user_id"]).delete()
            db.commit()
            print(f"{GREEN}[OK] Cleaned up test user {TEST_USER_EMAIL}{RESET}")
    except Exception as e:
        print(f"{RED}[ERROR] Cleanup failed: {e}{RESET}")
        db.rollback()
    finally:
        db.close()

# --- RUNNER ---

def run_e2e_tests():
    print(f"{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}RUNNING FITAVATAR E2E TEST SUITE{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    
    test_functions = [
        test_01_setup_profile,
        test_02_get_me,
        test_03_update_profile,
        test_04_generate_diet,
        test_05_get_latest_diet,
        test_06_record_session,
        test_07_get_sessions,
        test_08_get_progress
    ]
    
    results = []
    try:
        for test in test_functions:
            success = test()
            results.append(success)
            if not success:
                print(f"\n{RED}Stopping tests due to failure in {test.__name__}{RESET}")
                break
    finally:
        # Clear overrides
        app.dependency_overrides.clear()
        # Cleanup
        cleanup()
    
    passed_count = sum(results)
    total_count = len(test_functions)
    
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"E2E TEST SUMMARY: {passed_count}/{total_count} PASSED")
    print(f"{YELLOW}{'='*60}{RESET}")
    
    if passed_count == total_count:
        print(f"{GREEN}CONGRATULATIONS! ALL ENDPOINTS ARE FUNCTIONAL.{RESET}")
        return True
    else:
        print(f"{RED}E2E TEST FAILED.{RESET}")
        return False

if __name__ == "__main__":
    run_e2e_tests()
