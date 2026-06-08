from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.database.connection import get_db
from app.models.user import User
from app.auth.auth_bearer import get_current_user
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse
from app.services import employee_service

router = APIRouter()

@router.get("", response_model=EmployeeListResponse)
def list_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    employees, total = employee_service.get_all_employees(db, page, per_page, search, department)
    return EmployeeListResponse(
        employees=employees,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=math.ceil(total / per_page) if total else 1,
    )

@router.get("/departments")
def get_departments(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return {"departments": employee_service.get_departments(db)}

@router.get("/search")
def search_employees(
    query: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    employees, total = employee_service.get_all_employees(db, search=query)
    return {
        "employees": employees,
        "total": total,
    }

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return employee_service.get_employee_by_id(db, employee_id)

@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return employee_service.create_employee(db, data)

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return employee_service.update_employee(db, employee_id, data)

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    employee_service.delete_employee(db, employee_id)
    return {"message": "Employee deleted successfully."}
