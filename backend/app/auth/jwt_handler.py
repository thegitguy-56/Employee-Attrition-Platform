# backend/app/auth/jwt_handler.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Creates and verifies JWT (JSON Web Tokens) — the "passes" users get
#   after logging in.
#
# How JWT works (beginner explanation):
#   1. User logs in with email + password
#   2. Server verifies credentials
#   3. Server creates a token: a long string like "eyJhbGciOiJIUzI1NiIsIn..."
#   4. User stores this token (in browser localStorage)
#   5. Every future request includes this token in the header
#   6. Server checks the token is valid and hasn't expired
#   7. Server reads the user info FROM the token (no database lookup needed!)
#
# The token has 3 parts separated by dots:
#   HEADER.PAYLOAD.SIGNATURE
#   - Header: algorithm used
#   - Payload: your data (user_id, email, role, expiry time)
#   - Signature: proves it hasn't been tampered with
# ─────────────────────────────────────────────────────────────────────────────

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt    # python-jose library for JWT operations
from fastapi import HTTPException, status
from app.config import get_settings

settings = get_settings()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new JWT token containing the given data.
    
    What 'data' should contain:
        {
            "sub": "user@email.com",    # "sub" = subject = who this token is for
            "user_id": 1,
            "role": "admin",
            "full_name": "John Smith"
        }
    
    Returns: a JWT token string like "eyJhbGci..."
    """
    # Make a copy so we don't modify the original dict
    to_encode = data.copy()

    # Set expiry time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default: use setting from config (1440 minutes = 24 hours)
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Add expiry and issued-at time to the token payload
    to_encode.update({
        "exp": expire,                          # When token expires
        "iat": datetime.now(timezone.utc),      # When token was issued
    })

    # Create the token by encoding the data with our SECRET_KEY
    # ALGORITHM is the math formula (HS256 = HMAC with SHA-256)
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Checks if a token is valid and returns the data inside it.
    
    Raises HTTPException 401 if:
    - Token is expired
    - Token was tampered with
    - Token is malformed
    
    Returns: the payload dict (user_id, email, role, etc.)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
        # This header tells the client what kind of auth is expected
    )

    try:
        # Decode the token using our SECRET_KEY
        # jwt.decode will raise JWTError if token is invalid or expired
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # The "sub" field should contain the user's email
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        return payload

    except JWTError:
        # Any JWT error (expired, invalid signature, malformed) raises 401
        raise credentials_exception


def decode_token_no_verify(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes a token WITHOUT checking if it's expired.
    Useful for reading user info from an expired token (e.g., for refresh flows).
    
    Returns None if the token is completely malformed.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False}   # Skip expiry check
        )
        return payload
    except JWTError:
        return None
