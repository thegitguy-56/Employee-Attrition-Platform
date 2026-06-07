# backend/app/database/init_db.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   1. Creates all database tables (users, employees, predictions)
#   2. Creates the default admin user if no admin exists yet
#
# When to run it:
#   ONCE — the very first time you set up the project on a new machine/server.
#   After that, tables already exist — running it again won't duplicate anything.
#
# How to run it (from the backend/ folder):
#   python -m app.database.init_db
#
# Or from the attrition-platform/ root:
#   cd backend
#   python -m app.database.init_db
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os

# Add the backend directory to the Python path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.models.prediction import Prediction
from app.auth.password_handler import hash_password
from app.config import get_settings

settings = get_settings()


def create_tables():
    """
    Creates all database tables.
    
    Base.metadata.create_all() looks at all classes that inherit from Base
    (User, Employee, Prediction) and creates their corresponding tables
    in PostgreSQL if they don't already exist.
    
    It's SAFE to run multiple times — it won't recreate existing tables.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")
    print("  - users")
    print("  - employees") 
    print("  - predictions")


def create_admin_user():
    """
    Creates the default admin user if one doesn't exist already.
    
    Default credentials:
        Email:    admin@company.com
        Password: Admin@123
    
    IMPORTANT: Change these in your .env file before going to production!
    """
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(
            User.email == settings.ADMIN_EMAIL
        ).first()

        if existing_admin:
            print(f"✓ Admin user already exists: {settings.ADMIN_EMAIL}")
            return

        # Create the admin user
        admin_user = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            full_name=settings.ADMIN_NAME,
            role=UserRole.admin,
            is_active=True,
        )

        db.add(admin_user)    # Stage the new user
        db.commit()           # Save it to the database
        db.refresh(admin_user)  # Refresh to get the auto-assigned ID

        print(f"✓ Admin user created!")
        print(f"  Email:    {settings.ADMIN_EMAIL}")
        print(f"  Password: {settings.ADMIN_PASSWORD}")
        print(f"  Role:     admin")
        print(f"  ID:       {admin_user.id}")
        print()
        print("  ⚠️  IMPORTANT: Change the admin password after first login!")

    except Exception as e:
        db.rollback()   # Undo any changes if something went wrong
        print(f"✗ Error creating admin user: {e}")
        raise
    finally:
        db.close()   # Always close the session


def verify_connection():
    """
    Tests that we can actually connect to the database.
    Run this first to make sure your DATABASE_URL is correct.
    """
    try:
        db = SessionLocal()
        # Execute a simple query to test the connection
        db.execute(__import__('sqlalchemy').text("SELECT 1"))
        db.close()
        print(f"✓ Database connection successful!")
        print(f"  URL: {settings.DATABASE_URL[:50]}...")  # Only show first 50 chars for security
        return True
    except Exception as e:
        print(f"✗ Database connection failed!")
        print(f"  Error: {e}")
        print()
        print("  Troubleshooting:")
        print("  1. Check your DATABASE_URL in backend/.env")
        print("  2. Make sure your Neon database is running")
        print("  3. Check if your IP is whitelisted in Neon's settings")
        return False


def init_db():
    """
    Runs the full initialization: verify connection → create tables → create admin.
    """
    print("=" * 50)
    print("  Employee Attrition Platform — DB Init")
    print("=" * 50)
    print()

    # Step 1: Verify we can connect
    if not verify_connection():
        print("\nAborting — fix the database connection first.")
        sys.exit(1)

    print()

    # Step 2: Create tables
    create_tables()
    print()

    # Step 3: Seed admin user
    create_admin_user()

    print()
    print("=" * 50)
    print("  Database initialization complete!")
    print("  You can now start the backend server.")
    print("=" * 50)


# This block runs when you execute the file directly:
#   python -m app.database.init_db
# It WON'T run when this file is imported by another file.
if __name__ == "__main__":
    init_db()
