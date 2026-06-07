# backend/app/models/prediction.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Defines the "predictions" table — stores every prediction ever made.
#   This is our "audit log" — we can always look back and see:
#   "On what date did we predict employee X would leave? What was the risk?"
# ─────────────────────────────────────────────────────────────────────────────

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class Prediction(Base):
    """
    Represents the 'predictions' table.
    
    Every time someone runs a prediction (single or batch),
    we save the result here so it can be viewed in history.
    """

    __tablename__ = "predictions"

    # ── Identity ──────────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True)

    # ── Which Employee Was Predicted? ─────────────────────────────────────────
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    # ForeignKey links to the employees table.
    # nullable=True because batch predictions may not link to a saved employee.

    employee_name = Column(String(200), nullable=True)
    # Store name directly for easy display (so we don't need a JOIN every time)

    # ── Prediction Details ────────────────────────────────────────────────────
    model_used = Column(String(50), nullable=False)
    # Which ML model made this prediction:
    # "logistic_regression", "decision_tree", or "random_forest"

    attrition_prediction = Column(String(5), nullable=False)
    # The final answer: "Yes" (will leave) or "No" (will stay)

    risk_score = Column(Float, nullable=False)
    # Probability of leaving, as a decimal (e.g., 0.83 = 83% risk)

    # ── Explanation Data ──────────────────────────────────────────────────────
    key_factors = Column(JSON, nullable=True)
    # JSON list of the top reasons for this prediction.
    # Example: [{"factor": "OverTime", "impact": "high"}, ...]
    # Stored as JSON so we can save any structure

    recommendation = Column(Text, nullable=True)
    # The AI-generated text advice for HR.
    # Example: "High overtime detected. Recommend workload review."

    # ── Input Data Snapshot ───────────────────────────────────────────────────
    input_data = Column(JSON, nullable=True)
    # Save the employee data that was used for this prediction.
    # Useful for: "why was this prediction made?" investigations

    # ── Who Made This Prediction? ─────────────────────────────────────────────
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    # The user ID of the HR manager who ran this prediction

    created_by_name = Column(String(200), nullable=True)
    # Their name, stored for easy display

    # ── When? ─────────────────────────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ── Batch or Single? ──────────────────────────────────────────────────────
    is_batch = Column(Boolean, default=False)
    # True if this was part of a batch CSV upload
    # False if it was a single prediction

    batch_id = Column(String(50), nullable=True)
    # If is_batch=True, all predictions from the same CSV upload
    # share the same batch_id (so you can find them together)

    def __repr__(self):
        return f"<Prediction id={self.id} employee={self.employee_name} risk={self.risk_score:.1%}>"
