from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
import uuid
import io

from app.database.connection import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.auth.auth_bearer import get_current_user
from app.schemas.prediction_schema import PredictionRequest, PredictionResponse, BatchPredictionResponse
from app.services import ml_service
from app.services.employee_service import get_employee_by_id

router = APIRouter()

@router.post("/debug-single")
def debug_predict_single(request: dict, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Temporary debug endpoint — returns full traceback on error."""
    import traceback as tb
    from app.services.employee_service import get_employee_by_id
    emp_id = request.get("employee_id")
    emp = get_employee_by_id(db, emp_id)
    employee_data = {
        "age": emp.age, "gender": emp.gender, "marital_status": emp.marital_status,
        "education": emp.education, "distance_from_home": emp.distance_from_home,
        "department": emp.department, "job_role": emp.job_role, "job_level": emp.job_level,
        "monthly_income": emp.monthly_income, "overtime": emp.overtime,
        "business_travel": emp.business_travel, "job_satisfaction": emp.job_satisfaction,
        "environment_satisfaction": emp.environment_satisfaction,
        "relationship_satisfaction": emp.relationship_satisfaction,
        "work_life_balance": emp.work_life_balance, "job_involvement": emp.job_involvement,
        "performance_rating": emp.performance_rating,
        "num_companies_worked": emp.num_companies_worked,
        "total_working_years": emp.total_working_years,
        "years_at_company": emp.years_at_company,
        "years_in_current_role": emp.years_in_current_role,
        "years_since_last_promotion": emp.years_since_last_promotion,
        "years_with_curr_manager": emp.years_with_curr_manager,
        "training_times_last_year": emp.training_times_last_year,
        "percent_salary_hike": emp.percent_salary_hike,
    }
    try:
        result = ml_service.predict_single(employee_data, "all")
        return {"status": "ok", "risk_score": result["overall_risk_score"], "risk_level": result["risk_level"]}
    except Exception as e:
        return {"status": "error", "type": type(e).__name__, "msg": str(e), "traceback": tb.format_exc(), "employee_data": employee_data}


@router.post("/single", response_model=PredictionResponse)
def predict_single(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run attrition prediction for one employee."""
    if not ml_service.models_loaded():
        raise HTTPException(status_code=503, detail="ML models not loaded. Check server logs.")

    # If employee_id given, load their data from DB
    employee_data = request.model_dump(exclude={"employee_id", "model"})
    employee_name = None

    if request.employee_id:
        emp = get_employee_by_id(db, request.employee_id)
        employee_name = f"{emp.first_name} {emp.last_name}"
        # Map DB fields to prediction dict
        employee_data = {
            "age": emp.age, "gender": emp.gender, "marital_status": emp.marital_status,
            "education": emp.education, "distance_from_home": emp.distance_from_home,
            "department": emp.department, "job_role": emp.job_role, "job_level": emp.job_level,
            "monthly_income": emp.monthly_income, "overtime": emp.overtime,
            "business_travel": emp.business_travel, "job_satisfaction": emp.job_satisfaction,
            "environment_satisfaction": emp.environment_satisfaction,
            "relationship_satisfaction": emp.relationship_satisfaction,
            "work_life_balance": emp.work_life_balance, "job_involvement": emp.job_involvement,
            "performance_rating": emp.performance_rating,
            "num_companies_worked": emp.num_companies_worked,
            "total_working_years": emp.total_working_years,
            "years_at_company": emp.years_at_company,
            "years_in_current_role": emp.years_in_current_role,
            "years_since_last_promotion": emp.years_since_last_promotion,
            "years_with_curr_manager": emp.years_with_curr_manager,
            "training_times_last_year": emp.training_times_last_year,
            "percent_salary_hike": emp.percent_salary_hike,
        }

    result = ml_service.predict_single(employee_data, request.model or "all")

    # Save to prediction history
    pred_record = Prediction(
        employee_id=request.employee_id,
        employee_name=employee_name or "Manual Entry",
        model_used=request.model or "all",
        attrition_prediction=result["overall_prediction"],
        risk_score=result["overall_risk_score"],
        key_factors=result["key_risk_factors"],
        recommendation=result["recommendation"],
        input_data=employee_data,
        created_by=current_user.id,
        created_by_name=current_user.full_name,
        is_batch=False,
    )
    db.add(pred_record)
    db.commit()
    db.refresh(pred_record)

    return PredictionResponse(
        employee_name=employee_name,
        overall_prediction=result["overall_prediction"],
        overall_risk_score=result["overall_risk_score"],
        risk_level=result["risk_level"],
        model_results=result["model_results"],
        key_risk_factors=result["key_risk_factors"],
        recommendation=result["recommendation"],
        prediction_id=pred_record.id,
        created_at=pred_record.created_at,
        ensemble_prediction=result["overall_prediction"],
        ensemble_risk_score=result["overall_risk_score"],
        models=result["model_results"],
        key_factors=[f["description"] for f in result["key_risk_factors"]],
    )


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run predictions for a CSV file of employees."""
    if not ml_service.models_loaded():
        raise HTTPException(status_code=503, detail="ML models not loaded.")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse CSV file.")

    if df.empty:
        raise HTTPException(status_code=400, detail="CSV file is empty.")

    results = ml_service.predict_batch(df)
    batch_id = str(uuid.uuid4())[:8]

    # Save all results to history
    formatted_results = []
    for r in results:
        if r.get("error"):
            formatted_results.append(r)
            continue
        db.add(Prediction(
            employee_name=r["employee_name"],
            model_used="all",
            attrition_prediction=r["overall_prediction"],
            risk_score=r["risk_score"],
            recommendation=r["recommendation"],
            created_by=current_user.id,
            created_by_name=current_user.full_name,
            is_batch=True,
            batch_id=batch_id,
        ))
        r_copy = dict(r)
        r_copy["attrition_prediction"] = r["overall_prediction"]
        formatted_results.append(r_copy)
    db.commit()

    high   = sum(1 for r in results if r["risk_level"] == "High")
    medium = sum(1 for r in results if r["risk_level"] == "Medium")
    low    = sum(1 for r in results if r["risk_level"] == "Low")

    return BatchPredictionResponse(
        total_processed=len(results),
        high_risk_count=high,
        medium_risk_count=medium,
        low_risk_count=low,
        results=formatted_results,
        batch_id=batch_id,
    )


@router.get("/history")
def prediction_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return the most recent predictions."""
    records = (
        db.query(Prediction)
        .order_by(Prediction.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "employee_name": r.employee_name,
            "model_used": r.model_used,
            "attrition_prediction": r.attrition_prediction,
            "risk_score": r.risk_score,
            "recommendation": r.recommendation,
            "created_at": r.created_at,
            "created_by_name": r.created_by_name,
            "is_batch": r.is_batch,
        }
        for r in records
    ]
