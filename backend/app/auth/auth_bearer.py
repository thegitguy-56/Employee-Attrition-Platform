# backend/app/auth/auth_bearer.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Provides the "security guard" for protected API routes.
#   Any route that requires login uses these functions.
#
# How it works:
#   When a request comes in, FastAPI calls get_current_user().
#   That function reads the Authorization header, extracts the JWT token,
#   verifies it, looks up the user in the database, and returns the User object.
#   If anything fails, it returns 401 Unauthorized.
#
# Usage in routes:
#   @router.get("/me")
#   def get_me(current_user: User = Depends(get_current_user)):
#       return current_user
# ─────────────────────────────────────────────────────────────────────────────

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.auth.jwt_handler import verify_token
from app.models.user import User

# HTTPBearer is FastAPI's built-in class for extracting Bearer tokens from headers.
# It reads the "Authorization: Bearer eyJhbG..." header automatically.
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency that:
    1. Reads the JWT token from the Authorization header
    2. Verifies the token is valid and not expired
    3. Looks up the user in the database
    4. Returns the User object
    
    If anything goes wrong, raises HTTP 401 Unauthorized.
    
    Usage:
        @router.get("/protected-route")
        def my_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.full_name}"}
    """
    # Extract the token string from the Bearer credentials
    token = credentials.credentials

    # Verify the token and get the payload (data stored inside it)
    payload = verify_token(token)

    # Get the user's email from the token
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token — no subject found"
        )

    # Look up the user in the database
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Account may have been deleted."
        )

    # Check if the user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Contact an administrator."
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    A stricter guard — only allows Admin users.
    
    Usage:
        @router.post("/users")  # Only admins can create users
        def create_user(current_user: User = Depends(require_admin)):
            ...
    """
    role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role_val != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for this action."
        )
    return current_user


def get_optional_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> User | None:
    """
    Like get_current_user, but doesn't raise an error if no token is provided.
    Returns None if the user is not logged in.
    
    Useful for routes that work differently based on auth status.
    """
    if not credentials:
        return None

    try:
        payload = verify_token(credentials.credentials)
        email = payload.get("sub")
        if not email:
            return None
        return db.query(User).filter(User.email == email, User.is_active == True).first()
    except Exception:
        return None
