# backend/app/schemas/employee_schema.py
# ─────────────────────────────────────────────────────────────────────────────
# What this file does:
#   Defines the shape of employee data for API requests and responses.
#
# EmployeeCreate → for adding a new employee (POST request)
# EmployeeUpdate → for editing an employee (PUT request)  
# EmployeeResponse → for returning employee data (GET response)
# ─────────────────────────────────────────────────────────────────────────────

from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


# ── Base Employee (shared fields) ─────────────────────────────────────────────
# We put all shared fields in a Base class, then inherit from it.
# This avoids repeating the same fields in Create and Update.
class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    age: int
    gender: str
    marital_status: str
    education: int
    distance_from_home: int
    department: str
    job_role: str
    job_level: Optional[int] = None
    monthly_income: float
    percent_salary_hike: Optional[int] = None
    num_companies_worked: Optional[int] = None
    total_working_years: Optional[int] = None
    years_at_company: int
    years_in_current_role: Optional[int] = None
    years_since_last_promotion: Optional[int] = None
    years_with_curr_manager: Optional[int] = None
    overtime: str = "No"
    business_travel: Optional[str] = "Non-Travel"
    job_satisfaction: int = 3
    environment_satisfaction: Optional[int] = 3
    relationship_satisfaction: Optional[int] = 3
    work_life_balance: int = 3
    job_involvement: Optional[int] = 3
    performance_rating: int = 3
    training_times_last_year: Optional[int] = None
    employee_number: Optional[str] = None

    @field_validator("age")
    @classmethod
    def age_must_be_valid(cls, v):
        """Age must be between 18 and 70."""
        if not (18 <= v <= 70):
            raise ValueError("Age must be between 18 and 70")
        return v

    @field_validator("gender")
    @classmethod
    def gender_must_be_valid(cls, v):
        if v not in ["Male", "Female"]:
            raise ValueError("Gender must be 'Male' or 'Female'")
        return v

    @field_validator("overtime")
    @classmethod
    def overtime_must_be_valid(cls, v):
        if v not in ["Yes", "No"]:
            raise ValueError("Overtime must be 'Yes' or 'No'")
        return v

    @field_validator("job_satisfaction", "work_life_balance", "performance_rating")
    @classmethod
    def rating_must_be_1_to_4(cls, v):
        if not (1 <= v <= 4):
            raise ValueError("Rating must be between 1 and 4")
        return v

    @field_validator("monthly_income")
    @classmethod
    def income_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Monthly income must be positive")
        return v


# ── Create Employee ────────────────────────────────────────────────────────────
class EmployeeCreate(EmployeeBase):
    """
    Used when HR adds a NEW employee.
    Inherits all fields from EmployeeBase — no extra fields needed.
    """
    pass


# ── Update Employee ────────────────────────────────────────────────────────────
class EmployeeUpdate(BaseModel):
    """
    Used when HR EDITS an employee's details.
    ALL fields are Optional — you only send what you want to change.
    
    Example: To just change salary, send: {"monthly_income": 7500}
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    education: Optional[int] = None
    distance_from_home: Optional[int] = None
    department: Optional[str] = None
    job_role: Optional[str] = None
    job_level: Optional[int] = None
    monthly_income: Optional[float] = None
    percent_salary_hike: Optional[int] = None
    num_companies_worked: Optional[int] = None
    total_working_years: Optional[int] = None
    years_at_company: Optional[int] = None
    years_in_current_role: Optional[int] = None
    years_since_last_promotion: Optional[int] = None
    years_with_curr_manager: Optional[int] = None
    overtime: Optional[str] = None
    business_travel: Optional[str] = None
    job_satisfaction: Optional[int] = None
    environment_satisfaction: Optional[int] = None
    relationship_satisfaction: Optional[int] = None
    work_life_balance: Optional[int] = None
    job_involvement: Optional[int] = None
    performance_rating: Optional[int] = None
    training_times_last_year: Optional[int] = None


# ── Employee Response ──────────────────────────────────────────────────────────
class EmployeeResponse(EmployeeBase):
    """
    Sent back to the frontend when returning employee data.
    Adds the database-assigned fields (id, timestamps, etc.)
    """
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True   # Allows converting from SQLAlchemy objects


# ── Paginated Employee List Response ─────────────────────────────────────────
class EmployeeListResponse(BaseModel):
    """
    Wraps a list of employees with pagination info.
    Used by the GET /employees endpoint.
    """
    employees: List[EmployeeResponse]
    total: int        # Total number of matching employees (for pagination)
    page: int         # Current page number
    per_page: int     # How many per page
    total_pages: int  # Total number of pages
