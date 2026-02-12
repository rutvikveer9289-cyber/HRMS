"""
Overtime API Endpoints
Handles overtime calculation and approval
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.services.overtime_service import OvertimeService
from app.repositories.overtime_repository import OvertimeRepository
from app.schemas.schemas import OvertimeCalculateRequest, OvertimeRecordResponse, OvertimeApprovalRequest, MessageResponse
from app.models.employee import Employee

router = APIRouter(prefix="/overtime", tags=["Overtime"])

@router.post("/calculate", response_model=List[OvertimeRecordResponse])
async def calculate_overtime(
    request: OvertimeCalculateRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Calculate overtime from attendance records"""
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    overtime_service = OvertimeService(db)
    return overtime_service.calculate_overtime_from_attendance(
        emp_id=request.emp_id,
        start_date=request.start_date,
        end_date=request.end_date,
        overtime_rate=request.overtime_rate
    )

@router.get("/{emp_id}", response_model=List[OvertimeRecordResponse])
async def get_employee_overtime(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get overtime records for employee"""
    if current_user.role == "EMPLOYEE" and current_user.emp_id != emp_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    overtime_repo = OvertimeRepository(db)
    # Get last 3 months of overtime
    from datetime import date, timedelta
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    return overtime_repo.get_by_emp_date_range(emp_id, start_date, end_date)

@router.get("/pending/approvals", response_model=List[OvertimeRecordResponse])
async def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get all pending overtime approvals"""
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    overtime_repo = OvertimeRepository(db)
    return overtime_repo.get_pending_approvals()

@router.put("/approve", response_model=OvertimeRecordResponse)
async def approve_overtime(
    request: OvertimeApprovalRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Approve or reject overtime"""
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    overtime_service = OvertimeService(db)
    
    if request.action == "APPROVE":
        return overtime_service.approve_overtime(
            overtime_id=request.overtime_id,
            approved_by=current_user.emp_id,
            remarks=request.remarks
        )
    else:
        return overtime_service.reject_overtime(
            overtime_id=request.overtime_id,
            approved_by=current_user.emp_id,
            remarks=request.remarks or "Rejected"
        )

@router.get("/summary/{emp_id}/{month}/{year}")
async def get_overtime_summary(
    emp_id: str,
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get overtime summary for a month"""
    if current_user.role == "EMPLOYEE" and current_user.emp_id != emp_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    overtime_service = OvertimeService(db)
    return overtime_service.get_overtime_summary(emp_id, month, year)
