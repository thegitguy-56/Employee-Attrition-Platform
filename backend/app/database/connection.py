# backend/app/database/connection.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Sets up the "bridge" between Python and your PostgreSQL database.
#
# What is SQLAlchemy?
#   SQLAlchemy is a library that lets you work with databases using Python
#   objects instead of raw SQL queries.
#   Instead of writing: SELECT * FROM employees WHERE id = 5
#   You write Python:   db.query(Employee).filter(Employee.id == 5).first()
#   Much easier to read and maintain!
#
# What is a Session?
#   Think of a "session" like opening a tab in your browser.
#   You open it, do your work, then close it.
#   Each API request gets its own session (its own "tab" to the database).
# ─────────────────────────────────────────────────────────────────────────────

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# ── Create the Engine ─────────────────────────────────────────────────────────
# The "engine" is the actual connection to your database.
# It uses the DATABASE_URL from your .env file.
#
# connect_args={"check_same_thread": False} is needed for PostgreSQL async safety.
# pool_pre_ping=True checks if the connection is alive before using it
# (important for cloud databases like Neon which may disconnect after idle time).
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine_args = {
    "echo": settings.DEBUG,
}

if is_sqlite:
    engine_args["connect_args"] = connect_args
else:
    engine_args["pool_pre_ping"] = True
    engine_args["pool_size"] = 10
    engine_args["max_overflow"] = 20

engine = create_engine(
    settings.DATABASE_URL,
    **engine_args
)

# ── Create the Session Factory ────────────────────────────────────────────────
# SessionLocal is a "factory" — a blueprint for making database sessions.
# Every time we need to talk to the database, we create one session,
# use it, then close it.
SessionLocal = sessionmaker(
    autocommit=False,  # Don't save changes automatically — we confirm them manually
    autoflush=False,   # Don't send SQL to DB until we ask for it
    bind=engine,       # Connect sessions to our database engine
)

# ── Base Class for Models ─────────────────────────────────────────────────────
# All our database table classes (models) will "inherit" from this Base.
# SQLAlchemy uses Base to track all our tables and create them in the database.
Base = declarative_base()


# ── get_db() — The Dependency Function ───────────────────────────────────────
# This is a special function used by FastAPI's "dependency injection" system.
#
# How it works:
#   1. FastAPI calls get_db() automatically before each API request
#   2. It creates a fresh database session
#   3. The route function uses that session
#   4. After the request finishes, the session is CLOSED (even if an error occurred)
#
# The "yield" keyword makes this a "generator function".
# Everything before yield = setup. Everything after yield = cleanup.
# FastAPI handles the cleanup automatically.
def get_db():
    """
    FastAPI dependency that provides a database session.
    
    Usage in routes:
        @router.get("/employees")
        def get_employees(db: Session = Depends(get_db)):
            return db.query(Employee).all()
    """
    db = SessionLocal()
    try:
        yield db          # Give the session to the route function
    finally:
        db.close()        # Always close the session when done (prevents memory leaks)
