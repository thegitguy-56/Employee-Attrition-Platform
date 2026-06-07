# backend/app/schemas/user_schema.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Defines the "shape" of user data going IN and OUT of the API.
#
# Think of schemas like forms:
#   - UserCreate = the form you fill to CREATE a user (includes password)
#   - UserResponse = what the API sends BACK about a user (NO password!)
#   - LoginRequest = the login form (email + password)
#   - TokenResponse = what you get back after login (the JWT token)
#
# Why separate from the database model?
#   The database model stores hashed_password. We NEVER send passwords back
#   in API responses. Schemas let us control exactly what data is visible.
# ─────────────────────────────────────────────────────────────────────────────

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


# ── Login Request ─────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    """What the frontend sends when a user tries to log in."""
    email: EmailStr        # Pydantic validates this is a real email format
    password: str


# ── Token Response ─────────────────────────────────────────────────────────────
class TokenResponse(BaseModel):
    """What the API sends back after successful login."""
    access_token: str      # The JWT token (a long string)
    token_type: str = "bearer"  # Always "bearer" — standard JWT convention
    user: "UserResponse"   # Also include user info so frontend knows the role


# ── User Create (Admin creates new HR users) ──────────────────────────────────
class UserCreate(BaseModel):
    """Data needed to create a new user account."""
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.hr_manager  # Default to hr_manager if not specified

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        """
        Validates that the password is strong enough.
        Pydantic v2 calls this automatically when you create a UserCreate object.
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


# ── User Update ────────────────────────────────────────────────────────────────
class UserUpdate(BaseModel):
    """Fields that can be updated. All Optional = not required."""
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# ── Change Password ────────────────────────────────────────────────────────────
class ChangePasswordRequest(BaseModel):
    """Data needed to change a user's own password."""
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters")
        return v


# ── User Response (sent back to frontend) ────────────────────────────────────
class UserResponse(BaseModel):
    """
    What the API sends back when returning user info.
    Note: hashed_password is NOT included — we never expose passwords!
    """
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        # This tells Pydantic v2 that it can read from SQLAlchemy model objects.
        # Without this, Pydantic won't know how to convert db.query(User) results.


# Fix the forward reference (TokenResponse uses UserResponse before it's defined)
TokenResponse.model_rebuild()
