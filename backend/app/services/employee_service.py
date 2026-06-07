import math
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from app.models.employee import Employee
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate


def get_all_employees(db,page=1,per_page=10,search=None,department=None):
    q = db.query(Employee).filter(Employee.is_active==True)
    if search:
        t=f"%{search}%"
        q=q.filter(or_(Employee.first_name.ilike(t),Employee.last_name.ilike(t)))
    if department:
        q=q.filter(Employee.department==department)
    q=q.order_by(Employee.created_at.desc())
    total=q.count()
    employees=q.offset((page-1)*per_page).limit(per_page).all()
    return employees, total


def get_employee_by_id(db, employee_id):
    emp=db.query(Employee).filter(Employee.id==employee_id,Employee.is_active==True).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found.")
    return emp


def create_employee(db, data: EmployeeCreate):
    emp=Employee(**data.model_dump())
    db.add(emp); db.commit(); db.refresh(emp)
    return emp


def update_employee(db, employee_id, data: EmployeeUpdate):
    emp=get_employee_by_id(db,employee_id)
    for k,v in data.model_dump(exclude_unset=True).items():
        setattr(emp,k,v)
    db.commit(); db.refresh(emp)
    return emp


def delete_employee(db, employee_id):
    emp=get_employee_by_id(db,employee_id)
    emp.is_active=False; db.commit()
    return True


def get_departments(db):
    rows=db.query(Employee.department).filter(Employee.is_active==True).distinct().order_by(Employee.department).all()
    return [r[0] for r in rows if r[0]]


def get_employee_count(db):
    return db.query(Employee).filter(Employee.is_active==True).count()
