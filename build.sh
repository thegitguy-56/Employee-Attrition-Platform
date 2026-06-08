#!/usr/bin/env bash
# =============================================================
# build.sh — Render Build Script
# =============================================================
# Render runs this BEFORE starting the server.
# It trains the ML models from the CSV dataset and copies
# the .pkl files to where the backend expects them.
#
# Render Build Command (in dashboard): bash build.sh
# Render Start Command:                cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
# =============================================================

set -e  # Exit immediately if any command fails

echo ""
echo "============================================="
echo "  RENDER BUILD — Employee Attrition Platform"
echo "============================================="

# ── Step 1: Install backend Python dependencies ──────────────
echo ""
echo "[1/4] Installing backend dependencies..."
pip install -r backend/requirements.txt

# ── Step 2: Install ML pipeline dependencies ─────────────────
echo ""
echo "[2/4] Installing ML pipeline dependencies..."
pip install -r ml_pipeline/requirements.txt

# ── Step 3: Train ML models from the dataset ─────────────────
echo ""
echo "[3/4] Training ML models..."

# The pipeline saves .pkl files to ml_pipeline/models/
# We need them in backend/app/ml/models/
python -c "
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'ml_pipeline'))

# Run preprocessing + training
from preprocess import run_preprocessing
from train_models import train_all_models
from feature_importance import run_feature_importance

print('  → Preprocessing dataset...')
run_preprocessing()

print('  → Training all 3 models...')
train_all_models()

print('  → Computing feature importance...')
run_feature_importance()

print('  → Done training!')
"

# ── Step 4: Copy model files to backend ──────────────────────
echo ""
echo "[4/4] Copying model artifacts to backend..."

mkdir -p backend/app/ml/models

cp ml_pipeline/models/logistic_regression.pkl  backend/app/ml/models/
cp ml_pipeline/models/decision_tree.pkl        backend/app/ml/models/
cp ml_pipeline/models/random_forest.pkl        backend/app/ml/models/
cp ml_pipeline/models/scaler.pkl               backend/app/ml/models/
cp ml_pipeline/models/label_encoders.pkl       backend/app/ml/models/
cp ml_pipeline/models/feature_columns.pkl      backend/app/ml/models/
cp ml_pipeline/models/feature_importance.json  backend/app/ml/models/

echo ""
echo "  Model files copied:"
ls -lh backend/app/ml/models/

echo ""
echo "============================================="
echo "  BUILD COMPLETE ✓"
echo "  Server will start next..."
echo "============================================="
