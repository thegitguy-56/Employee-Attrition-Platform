# backend/app/schemas/prediction_schema.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Defines the shape of prediction request and response data.
# ─────────────────────────────────────────────────────────────────────────────

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Single Prediction Request ─────────────────────────────────────────────────
class PredictionRequest(BaseModel):
    """
    What the frontend sends to request an attrition prediction.
    These are all the features our ML model needs.
    """
    # If predicting for a saved employee, send their ID
    # (the backend will auto-fill their data)
    employee_id: Optional[int] = None

    # Or send all data manually for a new/unsaved employee:
    age: Optional[int] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    education: Optional[int] = None
    distance_from_home: Optional[int] = None
    department: Optional[str] = None
    job_role: Optional[str] = None
    job_level: Optional[int] = None
    monthly_income: Optional[float] = None
    percent_salary_hike: Optional[int] = None
    num_companies_worked: Optional[int] = None
    total_working_years: Optional[int] = None
    years_at_company: Optional[int] = None
    years_in_current_role: Optional[int] = None
    years_since_last_promotion: Optional[int] = None
    years_with_curr_manager: Optional[int] = None
    overtime: Optional[str] = None
    business_travel: Optional[str] = None
    job_satisfaction: Optional[int] = None
    environment_satisfaction: Optional[int] = None
    relationship_satisfaction: Optional[int] = None
    work_life_balance: Optional[int] = None
    job_involvement: Optional[int] = None
    performance_rating: Optional[int] = None
    training_times_last_year: Optional[int] = None
    stock_option_level: Optional[int] = None
    education_field: Optional[str] = None

    # Which model to use (optional — defaults to all 3)
    model: Optional[str] = "all"  # "all", "logistic_regression", "decision_tree", "random_forest"


# ── Single Model Result ────────────────────────────────────────────────────────
class ModelResult(BaseModel):
    """Result from one ML model."""
    model_name: str           # e.g., "Random Forest"
    prediction: str           # "Yes" or "No"
    risk_score: float         # e.g., 0.82 (82% chance of leaving)
    risk_percentage: float    # e.g., 82.0 (same value, as percentage for display)
    confidence: str           # "High", "Medium", "Low" based on score distance from 0.5


# ── Key Risk Factor ────────────────────────────────────────────────────────────
class RiskFactor(BaseModel):
    """One explanation factor for why this prediction was made."""
    factor: str         # Feature name e.g., "OverTime"
    value: Any          # The employee's actual value e.g., "Yes"
    impact: str         # "high", "medium", "low"
    description: str    # Human-readable explanation e.g., "Working overtime significantly increases attrition risk"


# ── Full Prediction Response ───────────────────────────────────────────────────
class PredictionResponse(BaseModel):
    """
    What the API sends back after running a prediction.
    Contains results from all 3 models + explanations.
    """
    employee_name: Optional[str] = None
    
    # Aggregate result (consensus of all 3 models)
    overall_prediction: str      # "Yes" or "No"
    overall_risk_score: float    # Average of all model scores
    risk_level: str              # "Low" (<40%), "Medium" (40-70%), "High" (>70%)
    
    # Individual model results
    model_results: List[ModelResult]
    
    # Why this prediction was made
    key_risk_factors: List[RiskFactor]
    
    # AI-generated HR recommendation text
    recommendation: str
    
    # Prediction ID (saved to database)
    prediction_id: Optional[int] = None
    created_at: Optional[datetime] = None


# ── Batch Prediction Row ───────────────────────────────────────────────────────
class BatchPredictionRow(BaseModel):
    """One row of results from a batch CSV prediction."""
    row_number: int
    employee_name: Optional[str] = None
    overall_prediction: str
    risk_score: float
    risk_level: str
    recommendation: str
    error: Optional[str] = None   # If this row had an error, describe it here


# ── Batch Prediction Response ─────────────────────────────────────────────────
class BatchPredictionResponse(BaseModel):
    """Response for a batch CSV prediction."""
    total_processed: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    results: List[BatchPredictionRow]
    batch_id: str


# ── Prediction History Item ───────────────────────────────────────────────────
class PredictionHistoryItem(BaseModel):
    """One item in the prediction history list."""
    id: int
    employee_name: Optional[str] = None
    model_used: str
    attrition_prediction: str
    risk_score: float
    recommendation: Optional[str] = None
    created_at: datetime
    created_by_name: Optional[str] = None
    is_batch: bool = False

    class Config:
        from_attributes = True
