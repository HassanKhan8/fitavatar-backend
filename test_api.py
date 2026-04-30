"""Comprehensive API Test Script for FitAvatar Backend"""
import sys
import os
sys.path.append(os.getcwd())

import json
from datetime import datetime
import httpx

# Use httpx directly for testing (avoids version issues)
from starlette.testclient import TestClient

from app.main import app

# Create test client
client = TestClient(app)

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_result(test_name, passed, details=""):
    status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    print(f"[{status}] {test_name}")
    if details:
        print(f"      {details}")

# ==============================================================================
# TEST 1: Health Endpoints (No Auth Required)
#// ==============================================================================
print("\n" + "=" * 60)
print("TEST 1: Health Endpoints")
print("=" * 60)

def test_health():
    response = client.get("/health")
    data = response.json()
    passed = response.status_code == 200 and data.get("status") == "ok"
    print_result("GET /health", passed, f"Status: {response.status_code}, Data: {data}")
    return passed

def test_root():
    response = client.get("/")
    data = response.json()
    passed = response.status_code == 200 and "FitAvatar" in data.get("message", "")
    print_result("GET /", passed, f"Status: {response.status_code}")
    return passed

# ==============================================================================
# TEST 2: Authentication - Validation Tests
# ==============================================================================
print("\n" + "=" * 60)
print("TEST 2: Authentication Validation Tests")
print("=" * 60)

def test_auth_invalid_email():
    """Test with invalid email format"""
    response = client.post("/auth/setup-profile", json={
        "email": "invalid-email",
        "name": "Test User",
        "age": 30,
        "weight_kg": 80,
        "height_cm": 180,
        "gender": "male",
        "goal": "Muscle Gain",
        "activity_level": "Moderately Active",
        "country": "USA"
    })
    passed = response.status_code == 422
    print_result("POST /auth/setup-profile (invalid email)", passed, f"Status: {response.status_code}")
    return passed

def test_auth_invalid_gender():
    """Test with invalid gender"""
    response = client.post("/auth/setup-profile", json={
        "email": "test@example.com",
        "name": "Test User",
        "age": 30,
        "weight_kg": 80,
        "height_cm": 180,
        "gender": "invalid",
        "goal": "Muscle Gain",
        "activity_level": "Moderately Active",
        "country": "USA"
    })
    passed = response.status_code == 422
    print_result("POST /auth/setup-profile (invalid gender)", passed, f"Status: {response.status_code}")
    return passed

def test_auth_invalid_goal():
    """Test with invalid goal"""
    response = client.post("/auth/setup-profile", json={
        "email": "test@example.com",
        "name": "Test User",
        "age": 30,
        "weight_kg": 80,
        "height_cm": 180,
        "gender": "male",
        "goal": "Invalid Goal",
        "activity_level": "Moderately Active",
        "country": "USA"
    })
    passed = response.status_code == 422
    print_result("POST /auth/setup-profile (invalid goal)", passed, f"Status: {response.status_code}")
    return passed

def test_auth_invalid_country():
    """Test with unsupported country"""
    response = client.post("/auth/setup-profile", json={
        "email": "test@example.com",
        "name": "Test User",
        "age": 30,
        "weight_kg": 80,
        "height_cm": 180,
        "gender": "male",
        "goal": "Muscle Gain",
        "activity_level": "Moderately Active",
        "country": "INVALID_COUNTRY"
    })
    passed = response.status_code == 422
    print_result("POST /auth/setup-profile (invalid country)", passed, f"Status: {response.status_code}")
    return passed

def test_auth_age_too_low():
    """Test with age below minimum"""
    response = client.post("/auth/setup-profile", json={
        "email": "test@example.com",
        "name": "Test User",
        "age": 5,
        "weight_kg": 80,
        "height_cm": 180,
        "gender": "male",
        "goal": "Muscle Gain",
        "activity_level": "Moderately Active",
        "country": "USA"
    })
    passed = response.status_code == 422
    print_result("POST /auth/setup-profile (age too low)", passed, f"Status: {response.status_code}")
    return passed

def test_auth_height_too_low():
    """Test with height below minimum"""
    response = client.post("/auth/setup-profile", json={
        "email": "test@example.com",
        "name": "Test User",
        "age": 30,
        "weight_kg": 80,
        "height_cm": 50,
        "gender": "male",
        "goal": "Muscle Gain",
        "activity_level": "Moderately Active",
        "country": "USA"
    })
    passed = response.status_code == 422
    print_result("POST /auth/setup-profile (height too low)", passed, f"Status: {response.status_code}")
    return passed

# ==============================================================================
# TEST 3: Session Endpoints - Validation Tests
# ==============================================================================
print("\n" + "=" * 60)
print("TEST 3: Session Validation Tests")
print("=" * 60)

# Need a test token - using bypass for validation tests
TEST_TOKEN = "test-token-for-validation"

def test_session_invalid_exercise():
    """Test with invalid exercise name"""
    response = client.post(
        "/sessions",
        json={
            "exercise_name": "Invalid Exercise",
            "total_reps": 20,
            "correct_reps": 18,
            "incorrect_reps": 2,
            "score_percent": 90.0,
            "duration_seconds": 120
        },
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    passed = response.status_code == 422
    print_result("POST /sessions (invalid exercise)", passed, f"Status: {response.status_code}")
    return passed

def test_session_score_too_high():
    """Test with score > 100"""
    response = client.post(
        "/sessions",
        json={
            "exercise_name": "Squats",
            "total_reps": 20,
            "correct_reps": 18,
            "incorrect_reps": 2,
            "score_percent": 101.0,
            "duration_seconds": 120
        },
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    passed = response.status_code == 422
    print_result("POST /sessions (score > 100)", passed, f"Status: {response.status_code}")
    return passed

def test_session_score_negative():
    """Test with negative score"""
    response = client.post(
        "/sessions",
        json={
            "exercise_name": "Squats",
            "total_reps": 20,
            "correct_reps": 18,
            "incorrect_reps": 2,
            "score_percent": -10.0,
            "duration_seconds": 120
        },
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    passed = response.status_code == 422
    print_result("POST /sessions (score < 0)", passed, f"Status: {response.status_code}")
    return passed

# ==============================================================================
# TEST 4: Auth Endpoints - No Token
# ==============================================================================
print("\n" + "=" * 60)
print("TEST 4: Auth Without Token")
print("=" * 60)

def test_auth_no_token_get_me():
    """Test GET /auth/me without token"""
    response = client.get("/auth/me")
    passed = response.status_code in [401, 403]
    print_result("GET /auth/me (no token)", passed, f"Status: {response.status_code}")
    return passed

def test_auth_no_token_get_profile():
    """Test PUT /auth/profile without token"""
    response = client.put("/auth/profile", json={"name": "New Name"})
    passed = response.status_code in [401, 403]
    print_result("PUT /auth/profile (no token)", passed, f"Status: {response.status_code}")
    return passed

def test_diet_no_token():
    """Test POST /diet/plan without token"""
    response = client.post("/diet/plan")
    passed = response.status_code in [401, 403]
    print_result("POST /diet/plan (no token)", passed, f"Status: {response.status_code}")
    return passed

def test_diet_latest_no_token():
    """Test GET /diet/latest without token"""
    response = client.get("/diet/latest")
    passed = response.status_code in [401, 403]
    print_result("GET /diet/latest (no token)", passed, f"Status: {response.status_code}")
    return passed

def test_sessions_no_token():
    """Test GET /sessions without token"""
    response = client.get("/sessions")
    passed = response.status_code in [401, 403]
    print_result("GET /sessions (no token)", passed, f"Status: {response.status_code}")
    return passed

def test_progress_no_token():
    """Test GET /progress without token"""
    response = client.get("/progress")
    passed = response.status_code in [401, 403]
    print_result("GET /progress (no token)", passed, f"Status: {response.status_code}")
    return passed

# ==============================================================================
# TEST 5: Invalid JWT Token
# ==============================================================================
print("\n" + "=" * 60)
print("TEST 5: Invalid JWT Token")
print("=" * 60)

INVALID_TOKEN = "invalid.jwt.token"

def test_auth_invalid_token_get_me():
    """Test GET /auth/me with invalid token"""
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    passed = response.status_code in [401, 403]
    print_result("GET /auth/me (invalid token)", passed, f"Status: {response.status_code}")
    return passed

def test_diet_invalid_token():
    """Test POST /diet/plan with invalid token"""
    response = client.post("/diet/plan", headers={"Authorization": "Bearer invalid.jwt.token"})
    passed = response.status_code in [401, 403]
    print_result("POST /diet/plan (invalid token)", passed, f"Status: {response.status_code}")
    return passed

def test_sessions_invalid_token():
    """Test GET /sessions with invalid token"""
    response = client.get("/sessions", headers={"Authorization": "Bearer invalid.jwt.token"})
    passed = response.status_code in [401, 403]
    print_result("GET /sessions (invalid token)", passed, f"Status: {response.status_code}")
    return passed

def test_progress_invalid_token():
    """Test GET /progress with invalid token"""
    response = client.get("/progress", headers={"Authorization": "Bearer invalid.jwt.token"})
    passed = response.status_code in [401, 403]
    print_result("GET /progress (invalid token)", passed, f"Status: {response.status_code}")
    return passed

# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================
def run_all_tests():
    """Run all tests in order"""
    
    results = []
    
    # Test 1: Health
    results.append(test_health())
    results.append(test_root())
    
    # Test 2: Auth Validation
    results.append(test_auth_invalid_email())
    results.append(test_auth_invalid_gender())
    results.append(test_auth_invalid_goal())
    results.append(test_auth_invalid_country())
    results.append(test_auth_age_too_low())
    results.append(test_auth_height_too_low())
    
    # Test 3: Session Validation  
    results.append(test_session_invalid_exercise())
    results.append(test_session_score_too_high())
    results.append(test_session_score_negative())
    
    # Test 4: No Token
    results.append(test_auth_no_token_get_me())
    results.append(test_auth_no_token_get_profile())
    results.append(test_diet_no_token())
    results.append(test_diet_latest_no_token())
    results.append(test_sessions_no_token())
    results.append(test_progress_no_token())
    
    # Test 5: Invalid Token
    results.append(test_auth_invalid_token_get_me())
    results.append(test_diet_invalid_token())
    results.append(test_sessions_invalid_token())
    results.append(test_progress_invalid_token())
    
    # Summary
    passed = sum(results)
    total = len(results)
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed}/{total} passed")
    print("=" * 60)
    
    if passed == total:
        print(f"{GREEN}ALL TESTS PASSED!{RESET}")
        return True
    else:
        print(f"{RED}{total - passed} TESTS FAILED{RESET}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FitAvatar Backend - API Test Suite")
    print("=" * 60)
    print("\nThis script tests:")
    print("  - Health endpoints")
    print("  - Authentication validation") 
    print("  - Session validation")
    print("  - Protected endpoints without token")
    print("  - Protected endpoints with invalid token")
    print("\nNote: Full authentication tests require valid Supabase JWT")
    print("=" * 60)
    
    run_all_tests()
