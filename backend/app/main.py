# backend/app/main.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   This is the MAIN entry point for the entire backend.
#   When you run "uvicorn app.main:app", Python starts here.
#
#   It does 4 things:
#   1. Creates the FastAPI application
#   2. Sets up CORS (allows the React frontend to talk to this backend)
#   3. Loads the ML models when the server starts
#   4. Registers all the route files (auth, employees, predictions, analytics)
#
# What is CORS?
#   CORS = Cross-Origin Resource Sharing
#   Browsers have a security rule: JavaScript on website-A cannot call API-B
#   UNLESS API-B explicitly says "I allow calls from website-A"
#   Our React app runs on localhost:5173 (or Vercel)
#   Our FastAPI runs on localhost:8000 (or Render)
#   Without CORS settings, the browser would block all requests!
# ─────────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import get_settings

settings = get_settings()

# Set up logging so we can see what's happening in the terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ── Startup / Shutdown Events ─────────────────────────────────────────────────
# @asynccontextmanager lets us run code WHEN THE SERVER STARTS and WHEN IT STOPS
# This is where we load the ML models into memory so they're ready to use.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Code before 'yield' runs at STARTUP.
    Code after 'yield' runs at SHUTDOWN.
    """
    # ── STARTUP ────────────────────────────────────────────────────────────
    logger.info("Starting Employee Attrition Platform API...")

    # Load ML models into memory
    # We load them ONCE at startup so every prediction request is fast.
    # (Loading from disk takes ~1 second — we don't want that per-request)
    try:
        from app.services.ml_service import load_models
        load_models()
        logger.info("✓ ML models loaded successfully")
    except Exception as e:
        logger.warning(f"⚠ Could not load ML models: {e}")
        logger.warning("  Predictions will fail until models are available.")
        logger.warning("  Make sure .pkl files are in backend/app/ml/models/")

    logger.info("✓ API ready to accept requests")

    yield  # ← Server is running. All requests are handled here.

    # ── SHUTDOWN ────────────────────────────────────────────────────────────
    logger.info("Shutting down Employee Attrition Platform API...")


# ── Create FastAPI App ────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Employee Attrition Prediction Platform
    
    Predict employee attrition using 3 ML models:
    - Logistic Regression
    - Decision Tree  
    - Random Forest
    
    ### Features:
    - JWT Authentication (Admin + HR Manager roles)
    - Employee CRUD operations
    - Single and batch attrition predictions
    - Analytics and reporting
    """,
    docs_url="/docs",        # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",      # ReDoc UI at http://localhost:8000/redoc
    lifespan=lifespan,       # Register our startup/shutdown handler
)


# ── CORS Middleware ────────────────────────────────────────────────────────────
# Parse the allowed origins from the config string
# Config value: "http://localhost:5173,http://localhost:3000"
# We split by comma to get a list: ["http://localhost:5173", "http://localhost:3000"]
allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # allow_origins=["*"] would allow ALL websites — DON'T do this in production!
    
    allow_credentials=True,
    # Allows cookies and Authorization headers to be sent with requests
    
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # Which HTTP methods are allowed
    
    allow_headers=["*"],
    # Which request headers are allowed ("*" = all headers including Authorization)
)


# ── Import and Register Routers ────────────────────────────────────────────────
# Each router file handles a group of related endpoints.
# We import them here and "include" them in the main app.
# prefix="/api/auth" means all routes in auth_routes.py start with /api/auth/
try:
    from app.routes import auth_routes, employee_routes, prediction_routes, analytics_routes

    app.include_router(
        auth_routes.router,
        prefix="/api/auth",
        tags=["Authentication"]   # Groups these endpoints in Swagger docs
    )

    app.include_router(
        employee_routes.router,
        prefix="/api/employees",
        tags=["Employees"]
    )

    app.include_router(
        prediction_routes.router,
        prefix="/api/predict",
        tags=["Predictions"]
    )

    app.include_router(
        analytics_routes.router,
        prefix="/api/analytics",
        tags=["Analytics"]
    )

    logger.info("✓ All routers registered")

except ImportError as e:
    logger.warning(f"Some routes not yet available: {e}")


# ── Health Check Endpoint ─────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple endpoint to verify the server is running.
    
    Test it: GET http://localhost:8000/health
    Expected response: {"status": "ok", "version": "1.0.0"}
    
    Deployment platforms (Render) use this to check if your app is alive.
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ── Root Endpoint ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint — just a welcome message.
    Visiting http://localhost:8000/ shows this.
    """
    return {
        "message": "Employee Attrition Prediction API",
        "docs": "/docs",
        "health": "/health",
    }


# ── Global Error Handler ───────────────────────────────────────────────────────
# This catches any unhandled exceptions and returns a clean JSON response
# instead of a cryptic Python traceback.
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again.",
            "type": type(exc).__name__
        }
    )
