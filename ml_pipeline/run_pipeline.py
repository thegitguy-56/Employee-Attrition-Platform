"""
ml_pipeline/run_pipeline.py
============================
PURPOSE: A single "one-click" script that runs the ENTIRE ML pipeline
         in the correct order:
           Step 1 → Preprocess data
           Step 2 → Train all 3 models
           Step 3 → Generate feature importance
           Step 4 → Test a sample prediction

HOW TO RUN (from the attrition-platform/ root folder):
  cd ml_pipeline
  python run_pipeline.py

OR from the root:
  python ml_pipeline/run_pipeline.py

WHAT IT PRODUCES in ml_pipeline/models/:
  ├── scaler.pkl              — The StandardScaler (for preprocessing new data)
  ├── feature_columns.pkl     — Column names in the correct order
  ├── feature_columns.json    — Same thing but human-readable
  ├── label_encoders.pkl      — LabelEncoders for categorical columns
  ├── logistic_regression.pkl — Trained Logistic Regression model
  ├── decision_tree.pkl       — Trained Decision Tree model
  ├── random_forest.pkl       — Trained Random Forest model
  ├── feature_importance.json — Top 10 feature importances from RF
  └── model_comparison.json   — Accuracy/F1 comparison of all 3 models

RUNTIME: ~1-2 minutes on a typical laptop.
"""

import os
import sys
import time

# ─────────────────────────────────────────────
# Make sure we can import from this directory
# ─────────────────────────────────────────────
# When running from a different directory, Python needs to know
# where our scripts are located.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def check_dataset_exists():
    """Check that the IBM HR dataset CSV is present before we start."""
    csv_path = os.path.join(current_dir, "data", "WA_Fn-UseC_-HR-Employee-Attrition.csv")
    if not os.path.exists(csv_path):
        print("\n DATASET NOT FOUND!")
        print(f"\n   Expected at: {csv_path}")
        print("\n   Please:")
        print("   1. Go to: https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset")
        print("   2. Download the CSV file")
        print("   3. Place it at: ml_pipeline/data/WA_Fn-UseC_-HR-Employee-Attrition.csv")
        print("\n   Then run this script again.\n")
        sys.exit(1)
    print(f" Dataset found: {csv_path}")
    return csv_path


def run_step(step_number: int, step_name: str, func):
    """Run a pipeline step with timing and error handling."""
    print(f"\n{'🔷 '*15}")
    print(f"  STEP {step_number}: {step_name}")
    print(f"{'🔷 '*15}")
    start = time.time()
    try:
        result = func()
        elapsed = time.time() - start
        print(f"\n   Step {step_number} completed in {elapsed:.1f}s")
        return result
    except Exception as e:
        print(f"\n   Step {step_number} FAILED: {e}")
        print("\n  Please fix the error above and re-run this script.")
        sys.exit(1)


def main():
    """Run the complete ML pipeline."""
    total_start = time.time()

    print("\n" + " "*18)
    print("  EMPLOYEE ATTRITION ML PIPELINE — FULL RUN")
    print(" "*18)
    print("\n  This script will:")
    print("  1️⃣  Load and preprocess the IBM HR dataset")
    print("  2️⃣  Train Logistic Regression, Decision Tree, Random Forest")
    print("  3️⃣  Generate feature importance rankings")
    print("  4️⃣  Run a sample prediction to verify everything works")
    print("\n  Starting now...\n")

    # ── Pre-check ────────────────────────────────────────────────────
    check_dataset_exists()

    # ── Step 1: Preprocess ───────────────────────────────────────────
    from preprocess import run_preprocessing
    run_step(1, "Data Preprocessing", run_preprocessing)

    # ── Step 2: Train Models ─────────────────────────────────────────
    from train_models import train_all_models
    run_step(2, "Model Training (all 3 models)", train_all_models)

    # ── Step 3: Feature Importance ───────────────────────────────────
    from feature_importance import run_feature_importance
    run_step(3, "Feature Importance Analysis", run_feature_importance)

    # ── Step 4: Test Prediction ───────────────────────────────────────
    from predict import run_test_prediction
    run_step(4, "Test Prediction (sample employee)", run_test_prediction)

    # ── Summary ───────────────────────────────────────────────────────
    total_elapsed = time.time() - total_start
    print("\n" + " "*18)
    print(f"   PIPELINE COMPLETE! (Total time: {total_elapsed:.1f}s)")
    print(" "*18)

    models_dir = os.path.join(current_dir, "models")
    print(f"\n   All model files saved to: {models_dir}")
    print(f"\n  FILES CREATED:")
    for f in sorted(os.listdir(models_dir)):
        size = os.path.getsize(os.path.join(models_dir, f))
        print(f"    • {f:<40} ({size/1024:.1f} KB)")

    print("\n  NEXT STEP:")
    print("  Copy the .pkl files to backend/app/ml/models/")
    print("  Then proceed to Task 3: Backend Core Setup\n")


if __name__ == "__main__":
    main()
