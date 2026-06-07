"""
ml_pipeline/train_models.py
============================
PURPOSE: Train 3 machine learning models on the preprocessed IBM HR dataset,
         evaluate each one, and save them as .pkl files for the backend to use.

MODELS TRAINED:
  1. Logistic Regression  — like a smart yes/no calculator
  2. Decision Tree        — like a flowchart of if/then rules
  3. Random Forest        — hundreds of decision trees voting together

WHY ALL 3?
  Different models have different strengths. The backend can let users
  pick which one they trust most for their predictions.

HOW TO RUN:
  python ml_pipeline/train_models.py
  (Make sure you ran preprocess.py first OR use run_pipeline.py)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# Import our preprocessing function
from preprocess import run_preprocessing

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


# ─────────────────────────────────────────────
# EVALUATION HELPER
# ─────────────────────────────────────────────
# After training each model, we measure how well it works using 4 metrics.
# Here's what each metric means in plain English:
#
# ACCURACY:   Out of ALL predictions made, what % were correct?
#             Example: 85% means 85 out of 100 were right.
#             ⚠️ Can be misleading with imbalanced data (if 84% don't leave,
#             even a model that always says "No" gets 84% accuracy!)
#
# PRECISION:  When the model SAYS an employee will leave, how often is it right?
#             High precision = fewer false alarms.
#             Example: 80% precision → if model flags 10 people, 8 actually leave.
#
# RECALL:     Out of employees who ACTUALLY leave, how many did the model catch?
#             High recall = fewer employees slipping through undetected.
#             Example: 70% recall → model finds 7 out of every 10 actual leavers.
#
# F1 SCORE:   The balance between Precision and Recall.
#             Best used when both false alarms AND missed cases matter.
#             Formula: 2 × (Precision × Recall) / (Precision + Recall)
#
# CONFUSION MATRIX:
#             A 2×2 table showing:
#               True Negatives  (predicted No,  actually No)   ✅
#               False Positives (predicted Yes, actually No)   ❌ false alarm
#               False Negatives (predicted No,  actually Yes)  ❌ missed a leaver
#               True Positives  (predicted Yes, actually Yes)  ✅

def evaluate_model(model_name: str, y_test, y_pred) -> dict:
    """
    Print and return evaluation metrics for a trained model.
    y_test = actual labels from test set
    y_pred = labels predicted by the model
    """
    accuracy  = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall    = recall_score(y_test, y_pred, zero_division=0)
    f1        = f1_score(y_test, y_pred, zero_division=0)
    cm        = confusion_matrix(y_test, y_pred)

    print(f"\n{'─'*50}")
    print(f"  📊 Results for: {model_name}")
    print(f"{'─'*50}")
    print(f"  Accuracy  : {accuracy:.4f}  ({accuracy*100:.1f}%)")
    print(f"  Precision : {precision:.4f}  ({precision*100:.1f}%)")
    print(f"  Recall    : {recall:.4f}  ({recall*100:.1f}%)")
    print(f"  F1 Score  : {f1:.4f}  ({f1*100:.1f}%)")
    print(f"\n  Confusion Matrix:")
    print(f"  ┌────────────────────────────────┐")
    print(f"  │ Predicted: No   │ Predicted: Yes │")
    print(f"  ├────────────────────────────────┤")
    print(f"  │ Actual No : {cm[0][0]:4}  │    {cm[0][1]:4}        │")
    print(f"  │ Actual Yes: {cm[1][0]:4}  │    {cm[1][1]:4}        │")
    print(f"  └────────────────────────────────┘")
    print(f"\n  Full Report:")
    print(classification_report(y_test, y_pred, target_names=["No Attrition", "Attrition"]))

    return {
        "model": model_name,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm.tolist()
    }


# ─────────────────────────────────────────────
# MODEL 1: LOGISTIC REGRESSION
# ─────────────────────────────────────────────
# What it is: A mathematical formula that takes all the input features,
# multiplies each by a learned "weight", adds them up, and squishes the
# result through a sigmoid function to get a probability between 0 and 1.
#
# Think of it as: a smart weighted average of all features that outputs
# "probability of leaving".
#
# Strengths: Fast, simple, very interpretable (you can see which features
# matter most by looking at coefficients).
# Weaknesses: Assumes a linear relationship between features and target.

def train_logistic_regression(X_train, y_train, X_test, y_test) -> dict:
    print("\n" + "="*55)
    print("  TRAINING: Logistic Regression")
    print("="*55)
    print("  ⏳ Training...")

    model = LogisticRegression(
        max_iter=1000,       # Give it enough iterations to converge
        random_state=42,     # Reproducibility
        class_weight="balanced"  # Handle class imbalance (more "No" than "Yes")
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = evaluate_model("Logistic Regression", y_test, y_pred)

    # Save model to disk
    path = os.path.join(MODELS_DIR, "logistic_regression.pkl")
    joblib.dump(model, path)
    print(f"  💾 Saved: models/logistic_regression.pkl")

    return metrics


# ─────────────────────────────────────────────
# MODEL 2: DECISION TREE
# ─────────────────────────────────────────────
# What it is: The model learns a series of IF/THEN rules by splitting
# the data based on the feature that best separates leavers from stayers.
#
# Example of what it learns:
#   IF OverTime = Yes AND JobSatisfaction <= 2:
#     → Likely to leave (75% of similar employees left)
#   ELSE IF YearsAtCompany < 2:
#     → Likely to leave (60% left)
#   ELSE:
#     → Likely to stay
#
# Strengths: Very easy to visualize and explain to non-technical managers.
# Weaknesses: Can "overfit" — memorize training data without generalizing.

def train_decision_tree(X_train, y_train, X_test, y_test) -> dict:
    print("\n" + "="*55)
    print("  TRAINING: Decision Tree")
    print("="*55)
    print("  ⏳ Training...")

    model = DecisionTreeClassifier(
        max_depth=10,            # Limit depth to prevent overfitting
        min_samples_split=20,    # Need at least 20 samples to split a node
        min_samples_leaf=10,     # Each leaf must have at least 10 samples
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = evaluate_model("Decision Tree", y_test, y_pred)

    path = os.path.join(MODELS_DIR, "decision_tree.pkl")
    joblib.dump(model, path)
    print(f"  💾 Saved: models/decision_tree.pkl")

    return metrics


# ─────────────────────────────────────────────
# MODEL 3: RANDOM FOREST
# ─────────────────────────────────────────────
# What it is: Trains 200 Decision Trees, each on a random subset of the
# data and a random subset of features. Then takes a majority vote.
#
# Why is this better than one Decision Tree?
# Each tree makes slightly different mistakes. When you average out 200
# imperfect trees, the mistakes cancel out and the good decisions remain.
# This is called "ensemble learning".
#
# Strengths: Usually the best accuracy, handles outliers well.
# Weaknesses: Slower to train, harder to explain than a single tree.
#
# This is our BEST model — we'll use its feature importances for the
# analytics dashboard.

def train_random_forest(X_train, y_train, X_test, y_test) -> dict:
    print("\n" + "="*55)
    print("  TRAINING: Random Forest")
    print("="*55)
    print("  ⏳ Training (this may take ~30 seconds)...")

    model = RandomForestClassifier(
        n_estimators=200,        # 200 trees in the forest
        max_depth=15,            # Limit tree depth
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1                # Use all CPU cores to speed up training
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = evaluate_model("Random Forest", y_test, y_pred)

    path = os.path.join(MODELS_DIR, "random_forest.pkl")
    joblib.dump(model, path)
    print(f"  💾 Saved: models/random_forest.pkl")

    return metrics


# ─────────────────────────────────────────────
# SAVE COMPARISON SUMMARY
# ─────────────────────────────────────────────

def save_model_comparison(all_metrics: list):
    """Save a JSON summary comparing all 3 models side by side."""
    path = os.path.join(MODELS_DIR, "model_comparison.json")
    with open(path, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\n  💾 Saved comparison: models/model_comparison.json")

    # Print a quick comparison table
    print("\n" + "="*65)
    print("  📊 MODEL COMPARISON SUMMARY")
    print("="*65)
    print(f"  {'Model':<25} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print(f"  {'─'*25} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")
    for m in all_metrics:
        print(f"  {m['model']:<25} {m['accuracy']:>10.4f} {m['precision']:>10.4f} {m['recall']:>10.4f} {m['f1_score']:>10.4f}")
    print("="*65)

    # Recommend the best model
    best = max(all_metrics, key=lambda x: x["f1_score"])
    print(f"\n  🏆 Best model by F1 Score: {best['model']} ({best['f1_score']:.4f})")


# ─────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────

def train_all_models():
    """Run preprocessing then train all 3 models."""
    os.makedirs(MODELS_DIR, exist_ok=True)

    print("\n" + "🚀 "*15)
    print("  EMPLOYEE ATTRITION ML TRAINING PIPELINE")
    print("🚀 "*15)

    # Run preprocessing to get train/test splits
    X_train, X_test, y_train, y_test, feature_columns = run_preprocessing()

    all_metrics = []

    # Train each model
    metrics_lr = train_logistic_regression(X_train, y_train, X_test, y_test)
    all_metrics.append(metrics_lr)

    metrics_dt = train_decision_tree(X_train, y_train, X_test, y_test)
    all_metrics.append(metrics_dt)

    metrics_rf = train_random_forest(X_train, y_train, X_test, y_test)
    all_metrics.append(metrics_rf)

    # Save comparison
    save_model_comparison(all_metrics)

    print("\n✅ All 3 models trained and saved!\n")
    print("   Files created in ml_pipeline/models/:")
    print("   • logistic_regression.pkl")
    print("   • decision_tree.pkl")
    print("   • random_forest.pkl")
    print("   • model_comparison.json")
    print("\n   Next step: run feature_importance.py\n")

    return all_metrics


if __name__ == "__main__":
    train_all_models()
