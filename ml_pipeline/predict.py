"""
ml_pipeline/predict.py
========================
PURPOSE: A utility that the BACKEND will use to predict attrition for
         a single employee. It:
           1. Takes raw employee data (as a Python dict)
           2. Applies the same preprocessing used during training
           3. Runs prediction through ALL 3 models
           4. Returns prediction (Yes/No) + risk score % for each model

WHY THIS FILE EXISTS:
  The backend (FastAPI) cannot run preprocess.py and train_models.py
  every time someone requests a prediction — that would take minutes!
  Instead, we SAVE the trained models and preprocessing artifacts to
  .pkl files, then load them once at startup and reuse them for every
  prediction in milliseconds.

HOW TO TEST:
  python ml_pipeline/predict.py
  (Make sure train_models.py has been run first)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Optional

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# ─────────────────────────────────────────────
# LOAD SAVED ARTIFACTS ONCE AT STARTUP
# ─────────────────────────────────────────────
# We load everything into memory at import time so that individual
# prediction calls are fast (no disk I/O per prediction).

def load_artifacts():
    """
    Load all saved ML artifacts from disk.
    Returns a dict containing all 3 models + scaler + feature columns + encoders.
    """
    def load(filename):
        path = os.path.join(MODELS_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"❌ Missing: models/{filename}\n"
                f"   Run run_pipeline.py first to generate all model files."
            )
        return joblib.load(path)

    print("📦 Loading ML artifacts from disk...")
    artifacts = {
        "logistic_regression": load("logistic_regression.pkl"),
        "decision_tree":       load("decision_tree.pkl"),
        "random_forest":       load("random_forest.pkl"),
        "scaler":              load("scaler.pkl"),
        "feature_columns":     load("feature_columns.pkl"),
        "label_encoders":      load("label_encoders.pkl"),
    }

    # Load feature importance for recommendations
    fi_path = os.path.join(MODELS_DIR, "feature_importance.json")
    if os.path.exists(fi_path):
        with open(fi_path) as f:
            artifacts["feature_importance"] = json.load(f)

    print("✅ All artifacts loaded successfully!")
    return artifacts


# ─────────────────────────────────────────────
# PREPROCESS A SINGLE EMPLOYEE DICT
# ─────────────────────────────────────────────

def preprocess_employee(employee_data: dict, artifacts: dict) -> np.ndarray:
    """
    Convert a raw employee dictionary into a scaled NumPy array
    ready for model prediction.
    
    IMPORTANT: We must apply EXACTLY the same transformations that were
    done during training:
      1. Only keep the columns the model was trained on
      2. Apply the SAME LabelEncoders for categorical columns
      3. Apply the SAME StandardScaler

    employee_data example:
    {
        "Age": 35,
        "BusinessTravel": "Travel_Rarely",
        "Department": "Sales",
        "DistanceFromHome": 10,
        "Education": 3,
        ...
    }
    """
    feature_columns  = artifacts["feature_columns"]
    scaler           = artifacts["scaler"]
    label_encoders   = artifacts["label_encoders"]

    # Convert the dict to a single-row DataFrame
    df = pd.DataFrame([employee_data])

    # ── Encode categorical columns using saved encoders ──────────────
    for col, encoder in label_encoders.items():
        if col == "Attrition":
            continue  # Skip the target column
        if col in df.columns:
            # Handle unseen categories gracefully
            val = str(df[col].iloc[0])
            if val in encoder.classes_:
                df[col] = encoder.transform([val])
            else:
                # If an unknown category appears, use 0 as a fallback
                df[col] = 0

    # ── Keep only the columns the model expects, in the right order ──
    # Fill in any missing columns with 0
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    df = df[feature_columns]  # Reorder to match training column order

    # ── Convert to numeric (safety check) ───────────────────────────
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    # ── Scale features ───────────────────────────────────────────────
    scaled = scaler.transform(df)

    return scaled


# ─────────────────────────────────────────────
# MAIN PREDICTION FUNCTION
# ─────────────────────────────────────────────

def predict_employee(employee_data: dict, artifacts: dict) -> dict:
    """
    Run attrition prediction for one employee using all 3 models.
    
    Returns a dict like:
    {
        "logistic_regression": {"prediction": "Yes", "risk_score": 72.4, "confidence": 0.724},
        "decision_tree":       {"prediction": "No",  "risk_score": 38.1, "confidence": 0.619},
        "random_forest":       {"prediction": "Yes", "risk_score": 68.9, "confidence": 0.689},
        "consensus":           "Yes",
        "average_risk_score":  59.8,
        "key_factors":         ["OverTime", "JobSatisfaction", "MonthlyIncome"]
    }
    
    RISK SCORE: The probability that the employee will leave (0-100%).
      - model.predict_proba() returns [[prob_no, prob_yes]]
      - We take prob_yes × 100 to get the risk score as a percentage.
    """
    # Preprocess the input
    X = preprocess_employee(employee_data, artifacts)

    results = {}
    model_names = ["logistic_regression", "decision_tree", "random_forest"]

    for name in model_names:
        model = artifacts[name]

        # predict() returns [0] or [1] — class label
        prediction_class = model.predict(X)[0]
        prediction_label = "Yes" if prediction_class == 1 else "No"

        # predict_proba() returns [[prob_class_0, prob_class_1]]
        # We want the probability of class 1 (= "Yes, will leave") as risk %
        proba = model.predict_proba(X)[0]
        risk_score = round(float(proba[1]) * 100, 1)

        results[name] = {
            "prediction": prediction_label,
            "risk_score": risk_score,
            "confidence": round(float(max(proba)), 4)
        }

    # ── Consensus: what do the majority of models say? ───────────────
    yes_count = sum(1 for r in results.values() if r["prediction"] == "Yes")
    consensus = "Yes" if yes_count >= 2 else "No"

    # ── Average risk score across all 3 models ───────────────────────
    avg_risk = round(
        sum(r["risk_score"] for r in results.values()) / 3, 1
    )

    # ── Key factors: top 3 feature importances (from Random Forest) ──
    key_factors = []
    if "feature_importance" in artifacts:
        top_features = artifacts["feature_importance"].get("top_10", [])
        key_factors = [f["feature"] for f in top_features[:3]]

    results["consensus"] = consensus
    results["average_risk_score"] = avg_risk
    results["key_factors"] = key_factors

    return results


# ─────────────────────────────────────────────
# TEST WITH A SAMPLE EMPLOYEE
# ─────────────────────────────────────────────

SAMPLE_EMPLOYEE = {
    # Demographics
    "Age": 32,
    "Gender": "Male",
    "MaritalStatus": "Single",
    "Education": 3,
    "EducationField": "Life Sciences",

    # Job details
    "Department": "Sales",
    "JobRole": "Sales Executive",
    "JobLevel": 2,
    "JobInvolvement": 2,
    "JobSatisfaction": 2,      # Low satisfaction — risk factor!

    # Compensation
    "MonthlyIncome": 4500,     # Below average — risk factor!
    "MonthlyRate": 14000,
    "DailyRate": 1100,
    "HourlyRate": 65,
    "PercentSalaryHike": 11,
    "StockOptionLevel": 0,

    # Work conditions
    "OverTime": "Yes",         # Works overtime — risk factor!
    "BusinessTravel": "Travel_Frequently",  # Frequent travel — risk factor!
    "WorkLifeBalance": 2,      # Below average — risk factor!
    "EnvironmentSatisfaction": 3,
    "RelationshipSatisfaction": 3,

    # Performance
    "PerformanceRating": 3,
    "TrainingTimesLastYear": 2,

    # Tenure
    "YearsAtCompany": 2,       # Short tenure — risk factor!
    "YearsInCurrentRole": 1,
    "YearsSinceLastPromotion": 1,
    "YearsWithCurrManager": 1,
    "TotalWorkingYears": 8,
    "NumCompaniesWorked": 4,   # Switched many companies — risk factor!

    # Location
    "DistanceFromHome": 25,    # Lives far away — risk factor!
}


def run_test_prediction():
    """Run a test prediction and display the results."""
    print("\n" + "="*55)
    print("  PREDICTION TEST")
    print("="*55)

    # Load all artifacts
    artifacts = load_artifacts()

    print("\n📋 Employee profile being tested:")
    print(f"   Age: {SAMPLE_EMPLOYEE['Age']}, Dept: {SAMPLE_EMPLOYEE['Department']}")
    print(f"   Salary: ${SAMPLE_EMPLOYEE['MonthlyIncome']:,}/month")
    print(f"   OverTime: {SAMPLE_EMPLOYEE['OverTime']}")
    print(f"   Job Satisfaction: {SAMPLE_EMPLOYEE['JobSatisfaction']}/4")
    print(f"   Years at Company: {SAMPLE_EMPLOYEE['YearsAtCompany']}")

    print("\n🔮 Running predictions through all 3 models...")
    results = predict_employee(SAMPLE_EMPLOYEE, artifacts)

    print(f"\n{'='*55}")
    print(f"  PREDICTION RESULTS")
    print(f"{'='*55}")

    for model_name in ["logistic_regression", "decision_tree", "random_forest"]:
        r = results[model_name]
        emoji = "🔴" if r["prediction"] == "Yes" else "🟢"
        print(f"  {emoji} {model_name.replace('_', ' ').title():<25} "
              f"→  {r['prediction']:<4}  (Risk: {r['risk_score']:>5.1f}%)")

    print(f"\n  {'─'*50}")
    consensus_emoji = "🔴" if results["consensus"] == "Yes" else "🟢"
    print(f"  {consensus_emoji} CONSENSUS (majority vote): {results['consensus']}")
    print(f"  📊 Average Risk Score: {results['average_risk_score']}%")
    print(f"  🎯 Key Risk Factors: {', '.join(results['key_factors'])}")
    print(f"{'='*55}\n")

    return results


if __name__ == "__main__":
    run_test_prediction()
