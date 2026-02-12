"""
Salary API Endpoints
Handles salary structure management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.services.salary_service import SalaryService
from app.schemas.schemas import SalaryStructureCreate, SalaryStructureResponse, MessageResponse
from app.models.employee import Employee

router = APIRouter(prefix="/salary", tags=["Salary"])

@router.post("/structure", response_model=SalaryStructureResponse, status_code=status.HTTP_201_CREATED)
async def create_salary_structure(
    salary_data: SalaryStructureCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Create new salary structure for employee"""
    # Only HR, SUPER_ADMIN, and CEO can create salary structures
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized to create salary structures")
    
    salary_service = SalaryService(db)
    return salary_service.create_salary_structure(
        emp_id=salary_data.emp_id,
        salary_data=salary_data.model_dump(),
        created_by=current_user.emp_id
    )

@router.get("/structure/{emp_id}", response_model=SalaryStructureResponse)
async def get_active_salary(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get active salary structure for employee"""
    # Employees can only view their own salary
    if current_user.role == "EMPLOYEE" and current_user.emp_id != emp_id:
        raise HTTPException(status_code=403, detail="Not authorized to view other employee's salary")
    
    salary_service = SalaryService(db)
    return salary_service.get_active_salary(emp_id)

@router.get("/history/{emp_id}", response_model=List[SalaryStructureResponse])
async def get_salary_history(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get salary history for employee"""
    # Employees can only view their own history
    if current_user.role == "EMPLOYEE" and current_user.emp_id != emp_id:
        raise HTTPException(status_code=403, detail="Not authorized to view other employee's salary history")
    
    salary_service = SalaryService(db)
    return salary_service.get_salary_history(emp_id)

@router.put("/structure/{salary_id}", response_model=SalaryStructureResponse)
async def update_salary_structure(
    salary_id: int,
    salary_data: dict,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Update existing salary structure"""
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized to update salary structures")
    
    salary_service = SalaryService(db)
    return salary_service.update_salary_structure(salary_id, salary_data)
