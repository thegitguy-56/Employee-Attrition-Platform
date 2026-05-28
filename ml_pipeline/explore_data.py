"""
ml_pipeline/explore_data.py
===========================
PURPOSE: This script loads the IBM HR Attrition dataset and prints
a full summary so you understand what data you're working with
BEFORE building any ML model.

Think of it as an "X-ray" of your dataset.

HOW TO RUN:
    cd attrition-platform/ml_pipeline
    python explore_data.py

EXPECTED OUTPUT: Summary tables printed in your terminal.
"""

import pandas as pd
import numpy as np
import os

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Define the path to your dataset
# ─────────────────────────────────────────────────────────────────────────────
# os.path.dirname(__file__) gives us the folder THIS script lives in.
# We then look for data/WA_Fn-UseC_-HR-Employee-Attrition.csv
# You must place the downloaded CSV inside ml_pipeline/data/

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "data", "WA_Fn-UseC_-HR-Employee-Attrition.csv")


def load_dataset(path: str) -> pd.DataFrame:
    """
    Tries to load the CSV from the given path.
    If the file doesn't exist, prints a helpful error message and exits.
    """
    if not os.path.exists(path):
        print("\n❌  ERROR: Dataset file not found!")
        print(f"   Expected location: {path}")
        print("\n   ► Download steps:")
        print("     1. Go to: https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset")
        print("     2. Click the Download button (requires free Kaggle account)")
        print("     3. Unzip the downloaded file")
        print("     4. Copy  WA_Fn-UseC_-HR-Employee-Attrition.csv")
        print("     5. Paste it into:  attrition-platform/ml_pipeline/data/")
        raise SystemExit(1)

    print(f"✅  Dataset found at: {path}")
    df = pd.read_csv(path)
    print(f"✅  Dataset loaded successfully.\n")
    return df


def section(title: str):
    """Prints a visual section header so the output is easy to read."""
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def explore(df: pd.DataFrame):
    """
    Runs all exploration steps on the dataframe.
    Each step prints something useful about the data.
    """

    # ─────────────────────────────────────────────────────────────────────
    # STEP 2: Basic shape — how many rows and columns?
    # ─────────────────────────────────────────────────────────────────────
    section("DATASET SHAPE")
    rows, cols = df.shape
    print(f"  Rows (employees)  : {rows}")
    print(f"  Columns (features): {cols}")

    # ─────────────────────────────────────────────────────────────────────
    # STEP 3: First 5 rows — see what the data looks like
    # ─────────────────────────────────────────────────────────────────────
    section("FIRST 5 ROWS")
    # pd.set_option expands the display so columns don't get cut off
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    print(df.head())

    # ─────────────────────────────────────────────────────────────────────
    # STEP 4: All column names — what features do we have?
    # ─────────────────────────────────────────────────────────────────────
    section("ALL COLUMN NAMES")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2}. {col}")

    # ─────────────────────────────────────────────────────────────────────
    # STEP 5: Data types — is each column numeric or text?
    # ─────────────────────────────────────────────────────────────────────
    section("COLUMN DATA TYPES")
    dtype_df = pd.DataFrame({
        "Column": df.dtypes.index,
        "Type": df.dtypes.values,
        "Sample Value": [df[col].iloc[0] for col in df.columns]
    })
    print(dtype_df.to_string(index=False))

    # ─────────────────────────────────────────────────────────────────────
    # STEP 6: Target variable distribution — how many Yes vs No?
    # ─────────────────────────────────────────────────────────────────────
    section("TARGET VARIABLE: Attrition (Yes = left, No = stayed)")
    counts = df["Attrition"].value_counts()
    total = len(df)
    for label, count in counts.items():
        pct = (count / total) * 100
        bar = "█" * int(pct / 2)  # simple ASCII bar chart
        print(f"  {label:3}  |  {bar:<30}  {count:4} employees  ({pct:.1f}%)")

    print(f"\n  ⚠️  NOTE: The dataset is IMBALANCED.")
    print(f"      'No' (stayed) is much more common than 'Yes' (left).")
    print(f"      We will handle this during model training with class_weight='balanced'.")

    # ─────────────────────────────────────────────────────────────────────
    # STEP 7: Missing values — are there any empty cells?
    # ─────────────────────────────────────────────────────────────────────
    section("MISSING VALUES PER COLUMN")
    missing = df.isnull().sum()
    total_missing = missing.sum()
    if total_missing == 0:
        print("  ✅  No missing values found! This dataset is clean.")
    else:
        print(f"  ⚠️  Found {total_missing} missing values:")
        print(missing[missing > 0].to_string())

    # ─────────────────────────────────────────────────────────────────────
    # STEP 8: Numeric column statistics — min, max, mean, etc.
    # ─────────────────────────────────────────────────────────────────────
    section("NUMERIC COLUMNS — STATISTICS")
    numeric_df = df.select_dtypes(include=[np.number])
    print(numeric_df.describe().round(2).to_string())

    # ─────────────────────────────────────────────────────────────────────
    # STEP 9: Categorical columns — what unique values exist?
    # ─────────────────────────────────────────────────────────────────────
    section("CATEGORICAL COLUMNS — UNIQUE VALUES")
    cat_cols = df.select_dtypes(include=["object"]).columns
    for col in cat_cols:
        unique_vals = df[col].unique()
        print(f"\n  {col} ({len(unique_vals)} unique values):")
        print(f"    {list(unique_vals)}")

    # ─────────────────────────────────────────────────────────────────────
    # STEP 10: Constant columns — columns with only 1 value (useless for ML)
    # ─────────────────────────────────────────────────────────────────────
    section("CONSTANT COLUMNS (only 1 unique value — should be dropped)")
    constant_cols = [col for col in df.columns if df[col].nunique() == 1]
    if constant_cols:
        for col in constant_cols:
            print(f"  ⚠️  {col}  →  value is always: {df[col].iloc[0]}")
        print("\n  These columns give no information to the model — drop them in preprocessing.")
    else:
        print("  ✅  No constant columns found.")

    # ─────────────────────────────────────────────────────────────────────
    # STEP 11: Attrition rate by Department
    # ─────────────────────────────────────────────────────────────────────
    section("ATTRITION RATE BY DEPARTMENT")
    dept_attrition = df.groupby("Department")["Attrition"].apply(
        lambda x: (x == "Yes").sum() / len(x) * 100
    ).round(1)
    for dept, rate in dept_attrition.items():
        bar = "█" * int(rate / 2)
        print(f"  {dept:<35}  {bar:<20}  {rate}%")

    # ─────────────────────────────────────────────────────────────────────
    # STEP 12: Attrition rate by Job Role
    # ─────────────────────────────────────────────────────────────────────
    section("ATTRITION RATE BY JOB ROLE")
    role_attrition = df.groupby("JobRole")["Attrition"].apply(
        lambda x: (x == "Yes").sum() / len(x) * 100
    ).round(1).sort_values(ascending=False)
    for role, rate in role_attrition.items():
        bar = "█" * int(rate / 2)
        print(f"  {role:<35}  {bar:<20}  {rate}%")

    # ─────────────────────────────────────────────────────────────────────
    # FINAL SUMMARY
    # ─────────────────────────────────────────────────────────────────────
    section("EXPLORATION COMPLETE — WHAT TO DO NEXT")
    print("  1. Review the column list — these become your ML features.")
    print("  2. Note constant columns — drop them in preprocessing.")
    print("  3. Note categorical columns — they need encoding before ML.")
    print("  4. Note the class imbalance — handle it with class_weight='balanced'.")
    print("  5. Now run:  python preprocess.py  (Task 2)")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# When you run `python explore_data.py`, Python starts here.
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  IBM HR ATTRITION DATASET — EXPLORATION SCRIPT")
    print("=" * 65)
    df = load_dataset(DATA_PATH)
    explore(df)
