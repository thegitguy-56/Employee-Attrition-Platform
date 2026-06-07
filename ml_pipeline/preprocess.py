"""
ml_pipeline/preprocess.py
=========================
PURPOSE: Clean and prepare the IBM HR Attrition dataset so it's ready
         for machine learning. This script handles:
           - Removing useless columns
           - Encoding text categories as numbers
           - Scaling numbers to a standard range
           - Splitting data into training and testing sets
           - Saving the scaler and column list for later use in the backend

RUN THIS FIRST before training any models.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import json

# ─────────────────────────────────────────────
# STEP 1: Load the raw CSV file
# ─────────────────────────────────────────────
# We tell pandas to read the CSV file row by row and store it as a
# DataFrame — think of it like an Excel spreadsheet in Python.

def load_data(csv_path: str) -> pd.DataFrame:
    """Load CSV from disk and return a DataFrame."""
    print(f"📂 Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"   ✅ Loaded {df.shape[0]} rows × {df.shape[1]} columns")
    return df


# ─────────────────────────────────────────────
# STEP 2: Drop columns that don't help prediction
# ─────────────────────────────────────────────
# These 4 columns exist in the IBM dataset but carry NO useful information:
#   EmployeeCount   — every row has value 1 (useless)
#   EmployeeNumber  — just a unique ID, not a pattern
#   Over18          — every row says 'Y' (useless)
#   StandardHours   — every row has value 80 (useless)
#
# Keeping them would confuse the model without helping it.

COLS_TO_DROP = ["EmployeeCount", "EmployeeNumber", "Over18", "StandardHours"]

def drop_useless_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove columns that carry no predictive value."""
    existing = [c for c in COLS_TO_DROP if c in df.columns]
    df = df.drop(columns=existing)
    print(f"   🗑  Dropped columns: {existing}")
    return df


# ─────────────────────────────────────────────
# STEP 3: Handle missing values
# ─────────────────────────────────────────────
# The IBM dataset is clean (no NaN values), but we handle this
# just in case someone uses a slightly different CSV version:
#   - Numeric columns: fill with the column's MEDIAN value
#     (median is more robust than mean when there are outliers)
#   - Text/category columns: fill with the most common value (mode)

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values so the model never sees NaN."""
    missing_count = df.isnull().sum().sum()
    if missing_count == 0:
        print("   ✅ No missing values found — dataset is clean!")
        return df

    print(f"   ⚠️  Found {missing_count} missing values — filling them in...")
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in ["float64", "int64"]:
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
    return df


# ─────────────────────────────────────────────
# STEP 4: Encode categorical (text) columns as numbers
# ─────────────────────────────────────────────
# Machine learning models work with NUMBERS, not text.
# So we convert things like:
#   "Male" → 1,  "Female" → 0
#   "Sales" → 2, "R&D" → 1,  "HR" → 0
#
# LabelEncoder does this automatically by sorting the unique values
# alphabetically and assigning 0, 1, 2, ...
#
# We also save what each encoding means so we can reverse it later
# (e.g., to display "Sales" in the frontend instead of "2").

def encode_categorical_columns(df: pd.DataFrame):
    """
    Convert all text columns to numbers using LabelEncoder.
    Returns the modified DataFrame plus a dict of {column: encoder_object}.
    """
    encoders = {}  # We'll save these so the backend can encode new inputs too

    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
    print(f"   🔤 Encoding {len(categorical_cols)} categorical columns: {categorical_cols}")

    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        print(f"      • {col}: {list(le.classes_)} → {list(range(len(le.classes_)))}")

    return df, encoders


# ─────────────────────────────────────────────
# STEP 5: Separate features (X) from the target label (y)
# ─────────────────────────────────────────────
# X = all the input columns (what we USE to predict)
# y = the Attrition column (what we WANT to predict: 0=No, 1=Yes)
#
# After LabelEncoding: Attrition "No" → 0, "Yes" → 1

def split_features_target(df: pd.DataFrame):
    """Split DataFrame into X (inputs) and y (output to predict)."""
    X = df.drop(columns=["Attrition"])
    y = df["Attrition"]
    print(f"   📊 Features (X): {X.shape[1]} columns")
    print(f"   🎯 Target (y) distribution:\n      {y.value_counts().to_dict()} (0=No attrition, 1=Yes attrition)")
    return X, y


# ─────────────────────────────────────────────
# STEP 6: Scale numerical features
# ─────────────────────────────────────────────
# Some columns have huge ranges (MonthlyIncome: 1009–19999) while others
# are tiny (WorkLifeBalance: 1–4). This difference in scale confuses
# models like Logistic Regression.
#
# StandardScaler transforms each column so that:
#   - Mean becomes 0
#   - Standard deviation becomes 1
# Example: [1000, 5000, 10000] → [-1.2, 0.1, 1.1]
#
# IMPORTANT: We fit the scaler on TRAINING DATA ONLY, then apply it to
# both train and test. This prevents "data leakage" (the test set should
# be treated as if we've never seen it).

def scale_features(X_train, X_test):
    """Scale features to zero-mean, unit-variance."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)   # Learn mean/std from TRAIN
    X_test_scaled  = scaler.transform(X_test)         # Apply same scaling to TEST
    print("   📏 Features scaled with StandardScaler")
    return X_train_scaled, X_test_scaled, scaler


# ─────────────────────────────────────────────
# STEP 7: Save the scaler and feature column list
# ─────────────────────────────────────────────
# The backend needs the SAME scaler and column order to process new
# employee data at prediction time. We save them as .pkl (pickle) files.
# Think of .pkl as a "snapshot" of a Python object saved to disk.

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

def save_preprocessing_artifacts(scaler, feature_columns: list, encoders: dict):
    """Save scaler, feature columns, and encoders to disk."""
    os.makedirs(MODELS_DIR, exist_ok=True)

    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    print(f"   💾 Saved: models/scaler.pkl")

    joblib.dump(feature_columns, os.path.join(MODELS_DIR, "feature_columns.pkl"))
    print(f"   💾 Saved: models/feature_columns.pkl")

    joblib.dump(encoders, os.path.join(MODELS_DIR, "label_encoders.pkl"))
    print(f"   💾 Saved: models/label_encoders.pkl")

    # Also save as JSON for easy inspection
    with open(os.path.join(MODELS_DIR, "feature_columns.json"), "w") as f:
        json.dump(feature_columns, f, indent=2)
    print(f"   💾 Saved: models/feature_columns.json")


# ─────────────────────────────────────────────
# MAIN FUNCTION — runs all steps in order
# ─────────────────────────────────────────────

def run_preprocessing(csv_path: str = None):
    """
    Master function — runs the full preprocessing pipeline.
    Returns: X_train, X_test, y_train, y_test, feature_columns
    """
    if csv_path is None:
        csv_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "WA_Fn-UseC_-HR-Employee-Attrition.csv"
        )

    print("\n" + "="*55)
    print("  STEP 1 — Load Dataset")
    print("="*55)
    df = load_data(csv_path)

    print("\n" + "="*55)
    print("  STEP 2 — Drop Useless Columns")
    print("="*55)
    df = drop_useless_columns(df)

    print("\n" + "="*55)
    print("  STEP 3 — Handle Missing Values")
    print("="*55)
    df = handle_missing_values(df)

    print("\n" + "="*55)
    print("  STEP 4 — Encode Categorical Columns")
    print("="*55)
    df, encoders = encode_categorical_columns(df)

    print("\n" + "="*55)
    print("  STEP 5 — Separate Features and Target")
    print("="*55)
    X, y = split_features_target(df)
    feature_columns = list(X.columns)

    print("\n" + "="*55)
    print("  STEP 6 — Train/Test Split (80% / 20%)")
    print("="*55)
    # random_state=42 ensures we get the SAME split every time we run
    # (reproducibility is important in ML experiments)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
        # stratify=y ensures both splits have the same Yes/No ratio
    )
    print(f"   Training set:  {X_train.shape[0]} rows")
    print(f"   Test set:      {X_test.shape[0]} rows")

    print("\n" + "="*55)
    print("  STEP 7 — Scale Features")
    print("="*55)
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)

    print("\n" + "="*55)
    print("  STEP 8 — Save Preprocessing Artifacts")
    print("="*55)
    save_preprocessing_artifacts(scaler, feature_columns, encoders)

    print("\n✅ Preprocessing complete!\n")
    return X_train_scaled, X_test_scaled, y_train, y_test, feature_columns


# ─────────────────────────────────────────────
# Entry point — run this file directly
# ─────────────────────────────────────────────
if __name__ == "__main__":
    run_preprocessing()
