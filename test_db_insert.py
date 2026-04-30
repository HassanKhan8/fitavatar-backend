
import sys
import os

# Add the current directory to sys.path so we can import 'app'
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User
from app.models.diet_log import DietLog
import uuid

def test_insert_diet_log():
    # 1. Create a database session
    db = SessionLocal()
    
    try:
        # 2. Find a user to link the diet log to
        # We'll take the first user in the database.
        user = db.query(User).first()
        
        if not user:
            print("[INFO] No users found in the database. Creating a test user first...")
            test_user = User(
                email="test_user@example.com",
                supabase_uid=str(uuid.uuid4()),
                name="Test User",
                age=25,
                weight_kg=70.0,
                height_cm=175.0,
                gender="male",
                goal="Maintenance",
                activity_level="Moderately Active",
                country="USA"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            user = test_user
            print(f"[SUCCESS] Created test user: {user.email} (ID: {user.id})")
        else:
            print(f"[INFO] Using existing user: {user.email} (ID: {user.id})")

        # 3. Create dummy diet log data
        new_log = DietLog(
            user_id=user.id,
            calories_target=2500,
            protein_target=150,
            bmi_value=22.8,
            bmi_category="Normal",
            goal=user.goal,
            location=user.country,
            meals_json={
                "breakfast": "Oatmeal with protein powder",
                "lunch": "Chicken salad",
                "dinner": "Grilled salmon with quinoa",
                "snacks": ["Apple", "Almonds"]
            }
        )

        # 4. Insert into database
        print("[ACTION] Attempting to insert diet log into Supabase...")
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        
        print("[SUCCESS] Successfully inserted diet log!")
        print(f"   Log ID: {new_log.id}")
        print(f"   Generated At: {new_log.generated_at}")

    except Exception as e:
        print(f"[ERROR] Error during insertion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_insert_diet_log()
