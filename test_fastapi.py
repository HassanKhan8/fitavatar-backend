try:
    from app.main import app
    print("FASTAPI APP IMPORTED SUCCESSFULLY")
    
    from app.database import engine, text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        print("DATABASE CONNECTIVITY VERIFIED")
except Exception as e:
    import traceback
    traceback.print_exc()
