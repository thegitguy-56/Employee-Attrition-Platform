# backend/app/models/user.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Defines the "users" table in the database.
#   Every person who can log into the platform is stored here.
#
# Think of this class as the blueprint for one row in the users table.
# When you do: User(email="hr@company.com", role="hr_manager")
# SQLAlchemy creates a new row with those values.
# ─────────────────────────────────────────────────────────────────────────────

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.database.connection import Base


# Define the allowed roles as an Enum
# An Enum is a fixed list of allowed values — prevents typos like "Adminn"
class UserRole(str, enum.Enum):
    admin = "admin"
    hr_manager = "hr_manager"


class User(Base):
    """
    Represents the 'users' table in PostgreSQL.
    
    Columns:
    - id          : Auto-numbered ID (1, 2, 3...) — primary key
    - email       : Login email address — must be unique
    - hashed_pwd  : The PASSWORD — stored as a hash, NEVER plain text!
    - full_name   : Display name of the user
    - role        : "admin" or "hr_manager"
    - is_active   : If False, user is deactivated (can't log in)
    - created_at  : Timestamp when user was created (auto-set)
    """

    __tablename__ = "users"   # This is the actual table name in PostgreSQL

    # Primary key — auto-incremented integer (1, 2, 3, ...)
    id = Column(Integer, primary_key=True, index=True)

    # Email — must be unique so two users can't have the same login
    email = Column(String(255), unique=True, nullable=False, index=True)
    # index=True makes searching by email MUCH faster

    # Hashed password — we NEVER store the real password!
    # We store a "hash" (scrambled version) and compare hashes when logging in
    hashed_password = Column(String(255), nullable=False)

    # Display name shown in the UI
    full_name = Column(String(255), nullable=False)

    # Role controls what the user can do
    # admin    → can do everything (create users, view all data)
    # hr_manager → can predict and view employees, but can't manage users
    role = Column(
        Enum(UserRole),
        default=UserRole.hr_manager,
        nullable=False
    )

    # If False, the user is "soft deleted" — they exist in DB but can't log in
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps — set automatically by the database
    # func.now() means "use the current database time"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        # This controls how the object looks when you print() it — for debugging
        return f"<User id={self.id} email={self.email} role={self.role}>"
