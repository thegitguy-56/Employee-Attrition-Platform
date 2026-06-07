# backend/app/models/employee.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Defines the "employees" table — stores all employee data.
#   These are the exact fields that our ML model was trained on
#   (same as the IBM HR dataset columns).
# ─────────────────────────────────────────────────────────────────────────────

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database.connection import Base


class Employee(Base):
    """
    Represents the 'employees' table in PostgreSQL.
    
    All fields match the IBM HR dataset so we can pass them
    directly to our ML models for prediction.
    """

    __tablename__ = "employees"

    # ── Identity ──────────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True)
    # Internal auto-ID used by the database

    employee_number = Column(Integer, unique=True, nullable=True)
    # The employee's company ID number (like a badge number)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    # Split name into two fields so we can sort/search by last name

    # ── Personal Info ─────────────────────────────────────────────────────────
    age = Column(Integer, nullable=False)
    # Age in years — ML model uses this for prediction

    gender = Column(String(20), nullable=False)
    # "Male" or "Female"

    marital_status = Column(String(20), nullable=False)
    # "Single", "Married", or "Divorced"

    education = Column(Integer, nullable=False)
    # 1=Below College, 2=College, 3=Bachelor, 4=Master, 5=Doctor

    distance_from_home = Column(Integer, nullable=False)
    # How far employee lives from office (in km)
    # Longer commutes → higher attrition risk

    # ── Job Info ──────────────────────────────────────────────────────────────
    department = Column(String(100), nullable=False)
    # e.g., "Sales", "Research & Development", "Human Resources"

    job_role = Column(String(100), nullable=False)
    # e.g., "Sales Executive", "Research Scientist", "Manager"

    job_level = Column(Integer, nullable=True)
    # 1=Entry, 2=Mid, 3=Senior, 4=Lead, 5=Executive

    monthly_income = Column(Float, nullable=False)
    # Monthly salary in dollars

    percent_salary_hike = Column(Integer, nullable=True)
    # Last salary increase percentage

    num_companies_worked = Column(Integer, nullable=True)
    # How many companies the employee has worked for before

    total_working_years = Column(Integer, nullable=True)
    # Total years of work experience

    years_at_company = Column(Integer, nullable=False)
    # How many years at THIS company

    years_in_current_role = Column(Integer, nullable=True)
    # How long in their current position

    years_since_last_promotion = Column(Integer, nullable=True)
    # If this is high → employee may feel stuck → higher attrition risk

    years_with_curr_manager = Column(Integer, nullable=True)
    # Years working with current manager

    # ── Work Conditions ───────────────────────────────────────────────────────
    overtime = Column(String(5), nullable=False, default="No")
    # "Yes" or "No" — working overtime increases attrition risk significantly

    business_travel = Column(String(50), nullable=True)
    # "Non-Travel", "Travel_Rarely", "Travel_Frequently"

    # ── Satisfaction Scores (all on 1-4 scale) ────────────────────────────────
    job_satisfaction = Column(Integer, nullable=False, default=3)
    # 1=Low, 2=Medium, 3=High, 4=Very High
    # Low satisfaction → high attrition risk

    environment_satisfaction = Column(Integer, nullable=True, default=3)
    # How happy the employee is with their work environment

    relationship_satisfaction = Column(Integer, nullable=True, default=3)
    # How happy the employee is with coworker relationships

    work_life_balance = Column(Integer, nullable=False, default=3)
    # 1=Bad, 2=Good, 3=Better, 4=Best
    # Poor work-life balance → higher attrition risk

    job_involvement = Column(Integer, nullable=True, default=3)
    # How engaged/involved the employee is in their work

    performance_rating = Column(Integer, nullable=False, default=3)
    # 3=Excellent, 4=Outstanding

    # ── Training ──────────────────────────────────────────────────────────────
    training_times_last_year = Column(Integer, nullable=True)
    # Number of training sessions attended last year

    # ── Soft Delete ───────────────────────────────────────────────────────────
    is_active = Column(Boolean, default=True, nullable=False)
    # Instead of deleting employees from the DB, we set this to False
    # This is called "soft delete" — data is preserved for auditing

    # ── Timestamps ───────────────────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Employee id={self.id} name={self.first_name} {self.last_name} dept={self.department}>"
