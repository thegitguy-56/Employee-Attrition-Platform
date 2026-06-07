# backend/app/auth/password_handler.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Handles password security — we NEVER store passwords in plain text.
#   Instead, we "hash" them (convert to a scrambled string).
#
# What is hashing?
#   Plain text password:  "Admin@123"
#   Hashed version:       "$2b$12$eJq7XoF3Kl5..."
#
#   Hashing is a ONE-WAY process:
#   - You CAN turn "Admin@123" → "$2b$12$..."
#   - You CANNOT turn "$2b$12$..." back to "Admin@123"
#
#   When a user logs in, we hash the entered password and COMPARE the two hashes.
#   If they match → correct password. We never see the real password.
#
# Why bcrypt?
#   bcrypt is slow on purpose — it takes ~100ms per hash.
#   This makes "brute force" attacks (trying millions of passwords) impractical.
# ─────────────────────────────────────────────────────────────────────────────

from passlib.context import CryptContext

# CryptContext is a helper from passlib library that manages hashing.
# schemes=["bcrypt"] means we use the bcrypt algorithm.
# deprecated="auto" means old hash formats are automatically upgraded.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Takes a plain text password and returns a secure hash.
    
    Example:
        hash_password("Admin@123") 
        → "$2b$12$eJq7XoF3Kl5wXY..." (60-character string)
    
    This hash is what we store in the database.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain text password matches a stored hash.
    
    Returns True if the password is correct, False otherwise.
    
    Example:
        verify_password("Admin@123", "$2b$12$eJq7XoF3...")  → True
        verify_password("wrongpass", "$2b$12$eJq7XoF3...")  → False
    
    How it works: bcrypt re-hashes the plain password and compares the results.
    """
    return pwd_context.verify(plain_password, hashed_password)
