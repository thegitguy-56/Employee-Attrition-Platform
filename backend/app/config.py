# config.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Reads all environment variables from the .env file and makes them
#   available to every other file in the backend.
#
# Why we need it:
#   We NEVER hardcode secrets (passwords, API keys) directly in code.
#   Instead, we store them in a .env file and read them here.
#   This way, the code is safe to share on GitHub — the secrets stay local.
# ─────────────────────────────────────────────────────────────────────────────

from pydantic_settings import BaseSettings  # Pydantic v2 way to read .env files
from functools import lru_cache             # Caches the settings so we only read .env once


class Settings(BaseSettings):
    """
    Each variable here maps to a line in your .env file.
    For example: DATABASE_URL=postgresql://... in .env
    becomes accessible as settings.DATABASE_URL in Python.
    """

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://user:password@localhost/attrition_db"
    # This is the full connection string to your Neon PostgreSQL database.
    # Format: postgresql://USERNAME:PASSWORD@HOST/DATABASE_NAME

    # ── JWT (Login Tokens) ────────────────────────────────────────────────────
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    # This is like a password used to sign login tokens.
    # If someone knows this key, they can fake a login — keep it secret!

    ALGORITHM: str = "HS256"
    # The math formula used to create tokens. HS256 is the standard choice.

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    # How long a login token lasts before it expires.
    # 1440 minutes = 24 hours. After this, the user must log in again.

    # ── CORS (Cross-Origin) ───────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    # Which websites are allowed to talk to this backend.
    # During development: your React app runs on localhost:5173
    # In production: replace with your Vercel URL (https://your-app.vercel.app)

    # ── App Info ──────────────────────────────────────────────────────────────
    APP_NAME: str = "Employee Attrition Prediction API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    # DEBUG=True shows detailed error messages. Set to False in production.

    # ── Admin User (created on first run) ─────────────────────────────────────
    ADMIN_EMAIL: str = "admin@company.com"
    ADMIN_PASSWORD: str = "Admin@123"
    ADMIN_NAME: str = "System Administrator"

    class Config:
        env_file = "backend/.env"          # Tell Pydantic to look for a .env file
        env_file_encoding = "utf-8"
        case_sensitive = True      # DATABASE_URL and database_url are different


@lru_cache()
def get_settings() -> Settings:
    """
    Returns the settings object.
    @lru_cache means Python only reads the .env file ONCE,
    then reuses the same object — faster and more efficient.
    
    Usage in other files:
        from app.config import get_settings
        settings = get_settings()
        print(settings.DATABASE_URL)
    """
    return Settings()
