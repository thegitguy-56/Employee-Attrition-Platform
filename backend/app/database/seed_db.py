# backend/app/database/seed_db.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   1. Cleans up existing seeded employees and prediction records.
#   2. Loads the trained ML models.
#   3. Generates 15 realistic employee records with varying attrition risks.
#   4. Predicts their attrition risk using the active ML model.
#   5. Inserts both the employees and predictions into the database.
#
# How to run it:
#   cd backend
#   python -m app.database.seed_db
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os

# Add the backend directory to the Python path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.models.employee import Employee
from app.models.prediction import Prediction
from app.models.user import User, UserRole
from app.services.ml_service import load_models, predict_single

# Data definition for seed employees
SEED_EMPLOYEES = [
    # --- HIGH RISK EMPLOYEES ---
    {
        "first_name": "Alice", "last_name": "Smith", "age": 24, "gender": "Female",
        "marital_status": "Single", "education": 2, "distance_from_home": 28,
        "department": "Sales", "job_role": "Sales Representative", "job_level": 1,
        "monthly_income": 2200.0, "percent_salary_hike": 11, "num_companies_worked": 4,
        "total_working_years": 3, "years_at_company": 1, "years_in_current_role": 1,
        "years_since_last_promotion": 0, "years_with_curr_manager": 1,
        "overtime": "Yes", "business_travel": "Travel_Frequently",
        "job_satisfaction": 1, "environment_satisfaction": 1, "relationship_satisfaction": 2,
        "work_life_balance": 1, "job_involvement": 1, "performance_rating": 3,
        "training_times_last_year": 1, "employee_number": "SEED-001"
    },
    {
        "first_name": "Charlie", "last_name": "Brown", "age": 29, "gender": "Male",
        "marital_status": "Single", "education": 3, "distance_from_home": 18,
        "department": "Research & Development", "job_role": "Laboratory Technician", "job_level": 1,
        "monthly_income": 2800.0, "percent_salary_hike": 12, "num_companies_worked": 5,
        "total_working_years": 5, "years_at_company": 2, "years_in_current_role": 1,
        "years_since_last_promotion": 2, "years_with_curr_manager": 1,
        "overtime": "Yes", "business_travel": "Travel_Rarely",
        "job_satisfaction": 1, "environment_satisfaction": 1, "relationship_satisfaction": 2,
        "work_life_balance": 2, "job_involvement": 2, "performance_rating": 3,
        "training_times_last_year": 2, "employee_number": "SEED-002"
    },
    {
        "first_name": "Evan", "last_name": "Wright", "age": 22, "gender": "Male",
        "marital_status": "Single", "education": 1, "distance_from_home": 25,
        "department": "Sales", "job_role": "Sales Representative", "job_level": 1,
        "monthly_income": 2100.0, "percent_salary_hike": 14, "num_companies_worked": 1,
        "total_working_years": 1, "years_at_company": 1, "years_in_current_role": 0,
        "years_since_last_promotion": 0, "years_with_curr_manager": 0,
        "overtime": "Yes", "business_travel": "Travel_Frequently",
        "job_satisfaction": 2, "environment_satisfaction": 1, "relationship_satisfaction": 1,
        "work_life_balance": 1, "job_involvement": 2, "performance_rating": 3,
        "training_times_last_year": 2, "employee_number": "SEED-003"
    },
    {
        "first_name": "Natalie", "last_name": "Portman", "age": 27, "gender": "Female",
        "marital_status": "Single", "education": 3, "distance_from_home": 20,
        "department": "Sales", "job_role": "Sales Executive", "job_level": 2,
        "monthly_income": 4100.0, "percent_salary_hike": 11, "num_companies_worked": 6,
        "total_working_years": 6, "years_at_company": 2, "years_in_current_role": 2,
        "years_since_last_promotion": 2, "years_with_curr_manager": 2,
        "overtime": "Yes", "business_travel": "Travel_Frequently",
        "job_satisfaction": 1, "environment_satisfaction": 2, "relationship_satisfaction": 2,
        "work_life_balance": 2, "job_involvement": 1, "performance_rating": 3,
        "training_times_last_year": 1, "employee_number": "SEED-004"
    },
    {
        "first_name": "Oliver", "last_name": "Twist", "age": 25, "gender": "Male",
        "marital_status": "Single", "education": 2, "distance_from_home": 15,
        "department": "Human Resources", "job_role": "Human Resources", "job_level": 1,
        "monthly_income": 2300.0, "percent_salary_hike": 13, "num_companies_worked": 3,
        "total_working_years": 4, "years_at_company": 1, "years_in_current_role": 1,
        "years_since_last_promotion": 0, "years_with_curr_manager": 1,
        "overtime": "Yes", "business_travel": "Travel_Rarely",
        "job_satisfaction": 1, "environment_satisfaction": 1, "relationship_satisfaction": 1,
        "work_life_balance": 1, "job_involvement": 2, "performance_rating": 3,
        "training_times_last_year": 2, "employee_number": "SEED-005"
    },

    # --- MEDIUM RISK EMPLOYEES ---
    {
        "first_name": "Fiona", "last_name": "Gallagher", "age": 31, "gender": "Female",
        "marital_status": "Married", "education": 3, "distance_from_home": 12,
        "department": "Research & Development", "job_role": "Research Scientist", "job_level": 2,
        "monthly_income": 4500.0, "percent_salary_hike": 15, "num_companies_worked": 2,
        "total_working_years": 8, "years_at_company": 4, "years_in_current_role": 3,
        "years_since_last_promotion": 3, "years_with_curr_manager": 3,
        "overtime": "Yes", "business_travel": "Travel_Rarely",
        "job_satisfaction": 2, "environment_satisfaction": 3, "relationship_satisfaction": 3,
        "work_life_balance": 2, "job_involvement": 3, "performance_rating": 3,
        "training_times_last_year": 3, "employee_number": "SEED-006"
    },
    {
        "first_name": "Hannah", "last_name": "Abbott", "age": 34, "gender": "Female",
        "marital_status": "Divorced", "education": 4, "distance_from_home": 14,
        "department": "Human Resources", "job_role": "Human Resources", "job_level": 2,
        "monthly_income": 4900.0, "percent_salary_hike": 14, "num_companies_worked": 3,
        "total_working_years": 9, "years_at_company": 5, "years_in_current_role": 3,
        "years_since_last_promotion": 4, "years_with_curr_manager": 3,
        "overtime": "No", "business_travel": "Travel_Rarely",
        "job_satisfaction": 2, "environment_satisfaction": 2, "relationship_satisfaction": 3,
        "work_life_balance": 2, "job_involvement": 3, "performance_rating": 3,
        "training_times_last_year": 2, "employee_number": "SEED-007"
    },
    {
        "first_name": "Laura", "last_name": "Croft", "age": 28, "gender": "Female",
        "marital_status": "Single", "education": 3, "distance_from_home": 10,
        "department": "Research & Development", "job_role": "Laboratory Technician", "job_level": 1,
        "monthly_income": 3200.0, "percent_salary_hike": 16, "num_companies_worked": 2,
        "total_working_years": 6, "years_at_company": 3, "years_in_current_role": 2,
        "years_since_last_promotion": 1, "years_with_curr_manager": 2,
        "overtime": "Yes", "business_travel": "Travel_Frequently",
        "job_satisfaction": 3, "environment_satisfaction": 2, "relationship_satisfaction": 4,
        "work_life_balance": 3, "job_involvement": 2, "performance_rating": 3,
        "training_times_last_year": 2, "employee_number": "SEED-008"
    },
    {
        "first_name": "Michael", "last_name": "Scott", "age": 42, "gender": "Male",
        "marital_status": "Married", "education": 3, "distance_from_home": 8,
        "department": "Sales", "job_role": "Sales Executive", "job_level": 3,
        "monthly_income": 7200.0, "percent_salary_hike": 12, "num_companies_worked": 3,
        "total_working_years": 15, "years_at_company": 7, "years_in_current_role": 5,
        "years_since_last_promotion": 4, "years_with_curr_manager": 4,
        "overtime": "Yes", "business_travel": "Travel_Rarely",
        "job_satisfaction": 3, "environment_satisfaction": 2, "relationship_satisfaction": 3,
        "work_life_balance": 2, "job_involvement": 3, "performance_rating": 3,
        "training_times_last_year": 3, "employee_number": "SEED-009"
    },

    # --- LOW RISK EMPLOYEES ---
    {
        "first_name": "Bob", "last_name": "Johnson", "age": 45, "gender": "Male",
        "marital_status": "Married", "education": 4, "distance_from_home": 3,
        "department": "Research & Development", "job_role": "Research Scientist", "job_level": 3,
        "monthly_income": 8500.0, "percent_salary_hike": 18, "num_companies_worked": 1,
        "total_working_years": 20, "years_at_company": 15, "years_in_current_role": 8,
        "years_since_last_promotion": 1, "years_with_curr_manager": 8,
        "overtime": "No", "business_travel": "Non-Travel",
        "job_satisfaction": 4, "environment_satisfaction": 4, "relationship_satisfaction": 4,
        "work_life_balance": 4, "job_involvement": 4, "performance_rating": 4,
        "training_times_last_year": 4, "employee_number": "SEED-010"
    },
    {
        "first_name": "Diana", "last_name": "Prince", "age": 38, "gender": "Female",
        "marital_status": "Married", "education": 4, "distance_from_home": 2,
        "department": "Sales", "job_role": "Manager", "job_level": 4,
        "monthly_income": 14500.0, "percent_salary_hike": 15, "num_companies_worked": 2,
        "total_working_years": 16, "years_at_company": 10, "years_in_current_role": 6,
        "years_since_last_promotion": 1, "years_with_curr_manager": 5,
        "overtime": "No", "business_travel": "Travel_Rarely",
        "job_satisfaction": 4, "environment_satisfaction": 4, "relationship_satisfaction": 4,
        "work_life_balance": 3, "job_involvement": 3, "performance_rating": 3,
        "training_times_last_year": 3, "employee_number": "SEED-011"
    },
    {
        "first_name": "George", "last_name": "Clooney", "age": 50, "gender": "Male",
        "marital_status": "Divorced", "education": 3, "distance_from_home": 5,
        "department": "Research & Development", "job_role": "Manufacturing Director", "job_level": 4,
        "monthly_income": 12500.0, "percent_salary_hike": 14, "num_companies_worked": 2,
        "total_working_years": 25, "years_at_company": 12, "years_in_current_role": 8,
        "years_since_last_promotion": 0, "years_with_curr_manager": 7,
        "overtime": "No", "business_travel": "Travel_Rarely",
        "job_satisfaction": 3, "environment_satisfaction": 4, "relationship_satisfaction": 4,
        "work_life_balance": 4, "job_involvement": 3, "performance_rating": 3,
        "training_times_last_year": 3, "employee_number": "SEED-012"
    },
    {
        "first_name": "Ian", "last_name": "Malcolm", "age": 55, "gender": "Male",
        "marital_status": "Married", "education": 5, "distance_from_home": 1,
        "department": "Research & Development", "job_role": "Research Director", "job_level": 5,
        "monthly_income": 19500.0, "percent_salary_hike": 20, "num_companies_worked": 3,
        "total_working_years": 32, "years_at_company": 18, "years_in_current_role": 12,
        "years_since_last_promotion": 2, "years_with_curr_manager": 10,
        "overtime": "No", "business_travel": "Non-Travel",
        "job_satisfaction": 4, "environment_satisfaction": 4, "relationship_satisfaction": 4,
        "work_life_balance": 3, "job_involvement": 4, "performance_rating": 4,
        "training_times_last_year": 2, "employee_number": "SEED-013"
    },
    {
        "first_name": "Julia", "last_name": "Roberts", "age": 36, "gender": "Female",
        "marital_status": "Married", "education": 3, "distance_from_home": 4,
        "department": "Research & Development", "job_role": "Healthcare Representative", "job_level": 2,
        "monthly_income": 6200.0, "percent_salary_hike": 13, "num_companies_worked": 1,
        "total_working_years": 10, "years_at_company": 8, "years_in_current_role": 6,
        "years_since_last_promotion": 1, "years_with_curr_manager": 5,
        "overtime": "No", "business_travel": "Travel_Rarely",
        "job_satisfaction": 4, "environment_satisfaction": 3, "relationship_satisfaction": 3,
        "work_life_balance": 3, "job_involvement": 3, "performance_rating": 3,
        "training_times_last_year": 3, "employee_number": "SEED-014"
    },
    {
        "first_name": "Kevin", "last_name": "Bacon", "age": 47, "gender": "Male",
        "marital_status": "Married", "education": 4, "distance_from_home": 2,
        "department": "Human Resources", "job_role": "Manager", "job_level": 4,
        "monthly_income": 15200.0, "percent_salary_hike": 17, "num_companies_worked": 2,
        "total_working_years": 24, "years_at_company": 15, "years_in_current_role": 10,
        "years_since_last_promotion": 3, "years_with_curr_manager": 9,
        "overtime": "No", "business_travel": "Travel_Rarely",
        "job_satisfaction": 4, "environment_satisfaction": 4, "relationship_satisfaction": 3,
        "work_life_balance": 4, "job_involvement": 4, "performance_rating": 3,
        "training_times_last_year": 4, "employee_number": "SEED-015"
    }
]


def seed_database():
    print("=" * 60)
    print("  Employee Attrition Platform - Database Seeding Script")
    print("=" * 60)
    print()

    db = SessionLocal()
    try:
        # Load ML models for predictions
        print("Loading ML models for risk predictions...")
        load_models()
        print("[OK] Models loaded successfully!")
        print()

        # Step 1: Query or create admin user for the "created_by" field
        admin = db.query(User).filter(User.role == UserRole.admin).first()
        if not admin:
            print("[WARNING] Default admin user not found in database. Please run init_db first.")
            return
        
        print(f"Using admin user: {admin.full_name} (ID: {admin.id})")
        print()

        # Step 2: Clean up existing seed data
        print("Cleaning up old seeded employees and predictions...")
        old_employees = db.query(Employee).filter(Employee.employee_number.like("SEED-%")).all()
        old_ids = [emp.id for emp in old_employees]
        if old_ids:
            # Delete predictions associated with seeded employees
            deleted_preds = db.query(Prediction).filter(Prediction.employee_id.in_(old_ids)).delete(synchronize_session=False)
            # Delete seeded employees
            deleted_emps = db.query(Employee).filter(Employee.id.in_(old_ids)).delete(synchronize_session=False)
            print(f"  -> Deleted {deleted_preds} old seed prediction records.")
            print(f"  -> Deleted {deleted_emps} old seed employee records.")
        else:
            print("  -> No old seed records found.")
        
        db.commit()
        print()

        # Step 3: Insert seed employees and compute actual predictions
        print("Inserting seed employees & generating attrition predictions...")
        employees_inserted = 0
        predictions_inserted = 0

        for emp_data in SEED_EMPLOYEES:
            # Create employee record
            employee = Employee(**emp_data)
            db.add(employee)
            db.flush()  # Flush to populate employee.id

            # Prepare data dictionary for ML prediction (using camelCase / lowercase format of ml_service)
            emp_dict = {
                "age": employee.age,
                "gender": employee.gender,
                "marital_status": employee.marital_status,
                "education": employee.education,
                "distance_from_home": employee.distance_from_home,
                "department": employee.department,
                "job_role": employee.job_role,
                "job_level": employee.job_level,
                "monthly_income": employee.monthly_income,
                "percent_salary_hike": employee.percent_salary_hike,
                "num_companies_worked": employee.num_companies_worked,
                "total_working_years": employee.total_working_years,
                "years_at_company": employee.years_at_company,
                "years_in_current_role": employee.years_in_current_role,
                "years_since_last_promotion": employee.years_since_last_promotion,
                "years_with_curr_manager": employee.years_with_curr_manager,
                "overtime": employee.overtime,
                "business_travel": employee.business_travel,
                "job_satisfaction": employee.job_satisfaction,
                "environment_satisfaction": employee.environment_satisfaction,
                "relationship_satisfaction": employee.relationship_satisfaction,
                "work_life_balance": employee.work_life_balance,
                "job_involvement": employee.job_involvement,
                "performance_rating": employee.performance_rating,
                "training_times_last_year": employee.training_times_last_year
            }

            # Generate prediction using Random Forest (or ensemble via 'all')
            pred_result = predict_single(emp_dict, model_name="all")
            
            # Save to prediction history
            prediction = Prediction(
                employee_id=employee.id,
                employee_name=f"{employee.first_name} {employee.last_name}",
                model_used="all",
                attrition_prediction=pred_result["overall_prediction"],
                risk_score=pred_result["overall_risk_score"],
                key_factors=pred_result["key_risk_factors"],
                recommendation=pred_result["recommendation"],
                input_data=emp_dict,
                created_by=admin.id,
                created_by_name=admin.full_name,
                is_batch=False
            )
            db.add(prediction)
            
            employees_inserted += 1
            predictions_inserted += 1
            print(f"  + Added: {employee.first_name} {employee.last_name} | Role: {employee.job_role} | Risk: {pred_result['overall_risk_score'] * 100:.1f}% ({pred_result['risk_level']})")

        db.commit()
        print()
        print(f"[OK] Seeding complete! Added {employees_inserted} employees and {predictions_inserted} prediction records.")
        print()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
