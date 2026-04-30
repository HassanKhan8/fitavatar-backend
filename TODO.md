# FitAvatar Backend - Comprehensive Test Plan

## App Overview
- **Framework**: FastAPI
- **Authentication**: Supabase JWT
- **Database**: PostgreSQL (Supabase)
- **ML Model**: PyTorch DietTensorModel

---

## Test Checklist

### Phase 1: Environment & Imports ✅❌

| Step | Test | Expected Result |
|------|------|-----------------|
| 1.1 | Import app config | DATABASE_URL loads successfully |
| 1.2 | Import database engine | Engine created with NullPool for port 6543 |
| 1.3 | Import FastAPI app | App instance created |
| 1.4 | Import all route modules | auth, diet, sessions, progress routes import |
| 1.5 | Import ML model | DietTensorModel loads |

---

### Phase 2: Database Connectivity ✅❌

| Step | Test | Expected Result |
|------|------|-----------------|
| 2.1 | Test direct DB connection | SELECT 1 returns result |
| 2.2 | Test SQLAlchemy connection | Engine.connect() succeeds |
| 2.3 | Create tables | All tables created without errors |
| 2.4 | Query existing tables | Tables accessible |

---

### Phase 3: Health Endpoints ✅❌

| Step | Endpoint | Method | Expected Result |
|------|----------|--------|-----------------|
| 3.1 | /health | GET | {"status": "ok", "service": "FitAvatar API"} |
| 3.2 | / | GET | Welcome message with docs link |

---

### Phase 4: Authentication Tests ✅❌

**Note**: Requires valid Supabase JWT token

| Step | Endpoint | Method | Test Data | Expected Result |
|------|----------|--------|----------|-----------------|
| 4.1 | /auth/setup-profile | POST | Valid profile data | 201 Created, user profile |
| 4.2 | /auth/setup-profile | POST | Duplicate email | 409 Conflict |
| 4.3 | /auth/me | GET | Valid JWT | 200, user profile |
| 4.4 | /auth/me | GET | No JWT | 401/403 Unauthorized |
| 4.5 | /auth/profile | PUT | Update fields | 200, updated profile |
| 4.6 | /auth/profile | PUT | Invalid country | 422 Validation Error |

**Test Validations**:
- Email format validation
- Gender must be "male" or "female"
- Goal must be: "Weight Loss", "Muscle Gain", "Maintenance"
- Age: 10-100, Weight: 20-300kg, Height: 100-250cm
- Country must be one of 15 supported countries

---

### Phase 5: Diet Endpoints Tests ✅❌

**Note**: Requires authenticated user

| Step | Endpoint | Method | Expected Result |
|------|----------|--------|-----------------|
| 5.1 | /diet/plan | POST | Generate diet plan, save to DB |
| 5.2 | /diet/latest | GET | Latest plan JSON |

**Response Validation**:
- bmi_value (float)
- bmi_profile (category string)
- daily_targets: {calories, protein}
- meals: {breakfast, lunch, snack, dinner}
- Each meal has 2 options with 3 foods each
- Food includes: name, grams, protein, calories

---

### Phase 6: Workout Session Tests ✅❌

| Step | Endpoint | Method | Test Data | Expected Result |
|------|----------|--------|----------|-----------------|
| 6.1 | /sessions | POST | Valid session data | 201 Created |
| 6.2 | /sessions | GET | - | List of sessions, total count |
| 6.3 | /sessions/{id} | GET | Valid ID | Session object |
| 6.4 | /sessions/{id} | GET | Invalid ID | 404 Not Found |
| 6.5 | /sessions | POST | Invalid exercise | 422 Validation Error |
| 6.6 | /sessions | POST | Invalid score (101) | 422 Validation Error |

**Exercise Options**: "Squats", "Push-ups", "Bicep Curls"
**Score Range**: 0-100%

---

### Phase 7: Progress Endpoint Tests ✅❌

| Step | Endpoint | Method | Expected Result |
|------|----------|--------|-----------------|
| 7.1 | /progress | GET | Full progress data |
| 7.2 | /progress/weekly | GET | Weekly summaries (last 8 weeks) |

**Response Validation**:
- All workout sessions
- Weekly summaries
- Complete user_progress history
- Diet plan history
- Aggregate stats

---

### Phase 8: ML Model Tests ✅❌

| Step | Test | Expected Result |
|------|------|-----------------|
| 8.1 | Load DietTensorModel | Model loads without errors |
| 8.2 | Load nutrient scaler | Scaler loads |
| 8.3 | BMI calculation | Correct BMI for weight/height |
| 8.4 | Compute targets (male) | Correct BMR calculation |
| 8.5 | Compute targets (female) | Correct BMR calculation |
| 8.6 | Score food | Returns 0-1 score |
| 8.7 | Generate meal plan | Plan with all meal types |

**BMI Categories**:
- < 18.5: Underweight
- 18.5-24.9: Normal
- 25.0-29.9: Overweight
- >= 30.0: Obese

---

### Phase 9: Integration Tests ✅❌

| Step | Scenario | Expected Result |
|------|----------|-----------------|
| 9.1 | Full auth flow: setup -> get profile -> update | All endpoints work |
| 9.2 | Diet flow: setup user -> generate plan -> get latest | Plan generated and retrieved |
| 9.3 | Session flow: save session -> get all -> get by id | Sessions saved and retrieved |
| 9.4 | Progress flow: sessions + diet -> get progress | Complete progress data |

---

### Phase 10: Error Handling Tests ✅❌

| Step | Test Case | Expected Result |
|------|----------|-----------------|
| 10.1 | Invalid JWT token | 401 Unauthorized |
| 10.2 | Expired JWT | 401 Unauthorized |
| 10.3 | No diet plan (GET /diet/latest) | 404 Not Found |
| 10.4 | Invalid session ID (GET) | 404 Not Found |
| 10.5 | Invalid weight (0 or negative) | 422 Validation Error |
| 10.6 | Invalid height (0 or negative) | 422 Validation Error |
| 10.7 | Missing required fields | 422 Validation Error |

---

## Test Data Examples

### Valid Profile Setup Request
```json
{
  "email": "test@example.com",
  "name": "John Doe",
  "age": 30,
  "weight_kg": 80.0,
  "height_cm": 180.0,
  "gender": "male",
  "goal": "Muscle Gain",
  "activity_level": "Moderately Active",
  "country": "USA"
}
```

### Valid Session Create
```json
{
  "exercise_name": "Squats",
  "total_reps": 20,
  "correct_reps": 18,
  "incorrect_reps": 2,
  "score_percent": 90.0,
  "duration_seconds": 120
}
```

---

## Supported Countries
Brazil, China, France, Greece, India, Italy, Japan, Lebanon, Mexico, Pakistan, Saudi Arabia, Spain, Thailand, Turkey, USA

---

## Test Execution Commands

```bash
# Quick smoke test
python test_fastapi.py

# Database debug
python debug_db.py

# Manual API testing
uvicorn app.main:app --reload

# Then visit http://localhost:8000/docs for Swagger UI
```

---

## Notes
- Phase 4+ requires valid Supabase JWT token
- Set DEBUG=true in .env for verbose logging
- Check DATABASE_URL environment variable is set
- Ensure SUPABASE_JWT_SECRET is configured
