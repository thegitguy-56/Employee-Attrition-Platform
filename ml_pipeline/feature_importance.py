"""
ml_pipeline/feature_importance.py
===================================
PURPOSE: Load the trained Random Forest model and extract which features
         (employee attributes) have the most influence on the attrition prediction.

WHAT IS FEATURE IMPORTANCE?
  After training a Random Forest, each feature gets a score (0 to 1) that
  represents: "How much did this feature help us split employees into
  leavers vs stayers?"

  Example result:
    OverTime             → 0.142  (14.2% of all decisions used this)
    MonthlyIncome        → 0.118  (11.8%)
    JobSatisfaction      → 0.089  ( 8.9%)
    ...

  This tells HR managers which factors to focus on to reduce attrition.
  The frontend shows this as a horizontal bar chart.

HOW TO RUN:
  python ml_pipeline/feature_importance.py
  (Make sure train_models.py has been run first)
"""

import os
import json
import joblib
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


def load_random_forest():
    """Load the saved Random Forest model from disk."""
    path = os.path.join(MODELS_DIR, "random_forest.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(
            "❌ random_forest.pkl not found!\n"
            "   Please run train_models.py first."
        )
    model = joblib.load(path)
    print("✅ Loaded Random Forest model")
    return model


def load_feature_columns():
    """Load the saved list of feature column names."""
    path = os.path.join(MODELS_DIR, "feature_columns.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(
            "❌ feature_columns.pkl not found!\n"
            "   Please run preprocess.py first."
        )
    columns = joblib.load(path)
    print(f"✅ Loaded {len(columns)} feature column names")
    return columns


def get_feature_importances(model, feature_columns: list) -> list:
    """
    Extract and sort feature importances from the Random Forest.
    
    model.feature_importances_ is a NumPy array of floats (one per feature).
    Higher value = more important for making decisions in the forest.
    All values sum to 1.0 (100%).
    
    Returns a sorted list of dicts: [{feature, importance, percentage}, ...]
    """
    importances = model.feature_importances_

    # Pair each feature name with its importance score
    paired = list(zip(feature_columns, importances))

    # Sort from most important to least important
    paired.sort(key=lambda x: x[1], reverse=True)

    # Format as a list of dictionaries for easy JSON export
    results = []
    for rank, (feature, importance) in enumerate(paired, start=1):
        results.append({
            "rank": rank,
            "feature": feature,
            "importance": round(float(importance), 6),
            "percentage": round(float(importance) * 100, 2)
        })

    return results


def print_top_features(importances: list, top_n: int = 10):
    """Print a formatted table of the top N most important features."""
    print(f"\n{'='*55}")
    print(f"  🏆 TOP {top_n} MOST IMPORTANT FEATURES FOR ATTRITION")
    print(f"{'='*55}")
    print(f"  {'Rank':<5} {'Feature':<30} {'Importance':>12}  {'Bar'}")
    print(f"  {'─'*5} {'─'*30} {'─'*12}  {'─'*20}")

    for item in importances[:top_n]:
        bar_length = int(item["percentage"] / 1.5)  # Scale for display
        bar = "█" * bar_length
        print(
            f"  {item['rank']:<5} {item['feature']:<30} "
            f"{item['percentage']:>10.2f}%  {bar}"
        )

    print(f"{'='*55}")
    print(f"\n  Total features: {len(importances)}")
    print(f"  Top {top_n} features account for: "
          f"{sum(x['percentage'] for x in importances[:top_n]):.1f}% of importance")


def save_feature_importance(importances: list):
    """Save the full feature importance list to a JSON file."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    output_path = os.path.join(MODELS_DIR, "feature_importance.json")

    # Save full list
    output_data = {
        "top_10": importances[:10],
        "all_features": importances,
        "note": "Extracted from Random Forest model. Higher = more influential."
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n  💾 Saved: models/feature_importance.json")
    print(f"      Contains rankings for all {len(importances)} features")


def run_feature_importance():
    """Main function — loads model, extracts importances, saves to JSON."""
    print("\n" + "="*55)
    print("  FEATURE IMPORTANCE ANALYSIS")
    print("="*55)

    model = load_random_forest()
    feature_columns = load_feature_columns()
    importances = get_feature_importances(model, feature_columns)
    print_top_features(importances, top_n=10)
    save_feature_importance(importances)

    print("\n✅ Feature importance analysis complete!\n")
    print("   This data will be shown in the Analytics dashboard")
    print("   as a horizontal bar chart showing which factors")
    print("   HR should focus on to reduce employee attrition.\n")

    return importances


if __name__ == "__main__":
    run_feature_importance()
