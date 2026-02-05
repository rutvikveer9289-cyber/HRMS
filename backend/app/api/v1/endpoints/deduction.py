"""
Deduction API Endpoints
Handles deduction type and employee deduction management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.repositories.deduction_repository import DeductionRepository
from app.schemas.schemas import DeductionTypeCreate, EmployeeDeductionCreate, MessageResponse
from app.models.employee import Employee
from datetime import date

router = APIRouter(prefix="/deductions", tags=["Deductions"])

@router.get("/types")
async def get_deduction_types(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get all active deduction types"""
    deduction_repo = DeductionRepository(db)
    return deduction_repo.get_all_deduction_types(active_only=True)

@router.post("/types", status_code=status.HTTP_201_CREATED)
async def create_deduction_type(
    deduction_data: DeductionTypeCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Create new deduction type"""
    if current_user.role not in ["HR", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    deduction_repo = DeductionRepository(db)
    return deduction_repo.create_deduction_type(deduction_data.model_dump())

@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_deduction_to_employee(
    deduction_data: EmployeeDeductionCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Assign deduction to employee"""
    if current_user.role not in ["HR", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    deduction_repo = DeductionRepository(db)
    return deduction_repo.create_employee_deduction(deduction_data.model_dump())

@router.get("/employee/{emp_id}")
async def get_employee_deductions(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get all active deductions for employee"""
    if current_user.role == "EMPLOYEE" and current_user.emp_id != emp_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    deduction_repo = DeductionRepository(db)
    return deduction_repo.get_active_deductions_by_emp_id(emp_id)

@router.delete("/{deduction_id}")
async def deactivate_employee_deduction(
    deduction_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Deactivate employee deduction"""
    if current_user.role not in ["HR", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    deduction_repo = DeductionRepository(db)
    deduction_repo.deactivate_employee_deduction(deduction_id, date.today())
    return {"message": "Deduction deactivated successfully"}
