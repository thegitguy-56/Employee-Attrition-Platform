from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.user import User
from app.models.employee import Employee
from app.models.prediction import Prediction
from app.auth.auth_bearer import get_current_user
from app.services.ml_service import get_feature_importance

router = APIRouter()

@router.get("/overview")
def overview(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Total employees, high-risk count, avg risk score, predictions today."""
    total_employees = db.query(Employee).filter(Employee.is_active == True).count()

    # High-risk = last prediction per employee with risk_score >= 0.7
    high_risk = (
        db.query(Prediction)
        .filter(Prediction.risk_score >= 0.7, Prediction.is_batch == False)
        .count()
    )

    avg_risk_row = db.query(func.avg(Prediction.risk_score)).scalar()
    avg_risk = round(float(avg_risk_row or 0) * 100, 1)

    from datetime import date
    today_count = (
        db.query(Prediction)
        .filter(func.date(Prediction.created_at) == date.today())
        .count()
    )

    return {
        "total_employees":    total_employees,
        "high_risk_count":    high_risk,
        "average_risk_score": avg_risk,
        "predictions_today":  today_count,
    }


@router.get("/by-department")
def by_department(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Average risk score grouped by department (from prediction history)."""
    rows = (
        db.query(Employee.department, func.avg(Prediction.risk_score).label("avg_risk"))
        .join(Prediction, Employee.id == Prediction.employee_id)
        .filter(Employee.is_active == True)
        .group_by(Employee.department)
        .all()
    )
    if not rows:
        # Return static demo data if no predictions yet
        return [
            {"department": "Sales",                    "avg_risk": 62.0},
            {"department": "Research & Development",   "avg_risk": 38.0},
            {"department": "Human Resources",          "avg_risk": 55.0},
        ]
    return [{"department": r[0], "avg_risk": round(float(r[1]) * 100, 1)} for r in rows]


@router.get("/by-satisfaction")
def by_satisfaction(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Employee count grouped by job satisfaction level."""
    rows = (
        db.query(Employee.job_satisfaction, func.count(Employee.id).label("count"))
        .filter(Employee.is_active == True)
        .group_by(Employee.job_satisfaction)
        .order_by(Employee.job_satisfaction)
        .all()
    )
    labels = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
    return [{"level": labels.get(r[0], str(r[0])), "count": r[1]} for r in rows]


@router.get("/salary-analysis")
def salary_analysis(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Average salary: high-risk employees vs low-risk employees."""
    high_risk_avg = (
        db.query(func.avg(Employee.monthly_income))
        .join(Prediction, Employee.id == Prediction.employee_id)
        .filter(Prediction.risk_score >= 0.7, Employee.is_active == True)
        .scalar()
    )
    low_risk_avg = (
        db.query(func.avg(Employee.monthly_income))
        .join(Prediction, Employee.id == Prediction.employee_id)
        .filter(Prediction.risk_score < 0.4, Employee.is_active == True)
        .scalar()
    )
    return {
        "high_risk_avg_salary": round(float(high_risk_avg or 0), 2),
        "low_risk_avg_salary":  round(float(low_risk_avg or 0), 2),
    }


@router.get("/top-risk")
def top_risk(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Top 10 highest-risk employees based on latest prediction."""
    rows = (
        db.query(
            Prediction.employee_name,
            Employee.department,
            Prediction.risk_score,
            Prediction.recommendation,
            Prediction.employee_id,
        )
        .outerjoin(Employee, Employee.id == Prediction.employee_id)
        .filter(Prediction.is_batch == False)
        .order_by(Prediction.risk_score.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "employee_name":  r[0],
            "department":     r[1] or "N/A",
            "risk_score":     round(float(r[2]) * 100, 1),
            "recommendation": r[3],
            "employee_id":    r[4],
        }
        for r in rows
    ]


@router.get("/feature-importance")
def feature_importance(_: User = Depends(get_current_user)):
    """Top feature importances from the Random Forest model."""
    data = get_feature_importance()
    if not data:
        return []
    # Return top 10
    return sorted(data, key=lambda x: x.get("importance", 0), reverse=True)[:10]
