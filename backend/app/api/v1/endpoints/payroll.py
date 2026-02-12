"""
Payroll API Endpoints
Handles payroll processing and payslip generation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.services.payroll_service import PayrollService
from app.services.pdf_service import PDFService
from app.repositories.payroll_repository import PayrollRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.schemas import PayrollProcessRequest, PayrollRecordResponse, MessageResponse, PayrollStatusUpdate, PayrollRecordUpdate
from app.models.employee import Employee
from datetime import date
router = APIRouter(prefix="/payroll", tags=["Payroll"])

@router.post("/process", response_model=PayrollRecordResponse, status_code=status.HTTP_201_CREATED)
async def process_payroll(
    request: PayrollProcessRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Process monthly payroll for employee"""
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized to process payroll")
    
    payroll_service = PayrollService(db)
    return payroll_service.process_payroll(
        emp_id=request.emp_id,
        month=request.month,
        year=request.year,
        processed_by=current_user.emp_id
    )

@router.post("/process-all/{month}/{year}")
async def process_all_payroll(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Process payroll for all employees for a month"""
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    from app.repositories.salary_repository import SalaryRepository
    salary_repo = SalaryRepository(db)
    payroll_service = PayrollService(db)
    
    # Get all employees with active salary
    active_salaries = salary_repo.get_all_active()
    results = []
    
    for salary in active_salaries:
        try:
            payroll = payroll_service.process_payroll(
                emp_id=salary.emp_id,
                month=month,
                year=year,
                processed_by=current_user.emp_id
            )
            results.append({"emp_id": salary.emp_id, "status": "success"})
        except Exception as e:
            results.append({"emp_id": salary.emp_id, "status": "failed", "error": str(e)})
    
    return {"processed": len(results), "results": results}

@router.get("/list/{month}/{year}", response_model=List[PayrollRecordResponse])
async def get_payroll_list(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get all payroll records for a month"""
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payroll_service = PayrollService(db)
    return payroll_service.get_payroll_list(month=month, year=year)

@router.get("/all", response_model=List[PayrollRecordResponse])
async def get_all_payroll(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get all payroll records ever processed"""
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payroll_service = PayrollService(db)
    return payroll_service.get_all_payroll()

@router.get("/{emp_id}/{month}/{year}", response_model=PayrollRecordResponse)
async def get_payroll_record(
    emp_id: str,
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get payroll record for employee"""
    if current_user.role == "EMPLOYEE" and current_user.emp_id != emp_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payroll_service = PayrollService(db)
    return payroll_service.get_payroll_record(emp_id, month, year)

@router.get("/download/{payroll_id}")
async def download_payslip(
    payroll_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Download payslip PDF"""
    payroll_repo = PayrollRepository(db)
    payroll = payroll_repo.get_by_id(payroll_id)
    
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    
    # Check authorization
    if current_user.role == "EMPLOYEE" and current_user.emp_id != payroll.emp_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get employee data
    employee_repo = EmployeeRepository(db)
    employee = employee_repo.get_by_emp_id(payroll.emp_id)
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee_data = {
        "full_name": employee.full_name,
        "email": employee.email,
        "designation": employee.designation,
        "department": employee.department or "N/A",
        "location": employee.location or "N/A",
        "bank_name": employee.bank_name or "N/A",
        "bank_account_no": employee.bank_account_no or "N/A"
    }
    
    # Generate PDF
    pdf_service = PDFService()
    pdf_buffer = pdf_service.generate_payslip(payroll, employee_data)
    
    # Return as downloadable file
    filename = f"Payslip_{payroll.emp_id}_{payroll.month:02d}_{payroll.year}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.put("/status/{payroll_id}")
async def update_payment_status(
    payroll_id: int,
    request: PayrollStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Update payroll payment status"""
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if request.status not in ["DRAFT", "PROCESSED", "PAID"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    payroll_service = PayrollService(db)
    return payroll_service.update_payment_status(
        payroll_id, 
        request.status, 
        request.payment_date,
        request.payment_method,
        request.transaction_id,
        request.utr_number
    )

@router.get("/employee/{emp_id}", response_model=List[PayrollRecordResponse])
async def get_employee_payroll_history(
    emp_id: str,
    limit: int = 12,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get payroll history for employee"""
    if current_user.role == "EMPLOYEE" and current_user.emp_id != emp_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payroll_repo = PayrollRepository(db)
    return payroll_repo.get_by_emp_id(emp_id, limit=limit)

@router.put("/{payroll_id}", response_model=PayrollRecordResponse)
async def update_payroll_details(
    payroll_id: int,
    request: PayrollRecordUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Update processed payroll record (earnings/deductions)"""
    if current_user.role not in ["HR", "SUPER_ADMIN", "CEO"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payroll_service = PayrollService(db)
    return payroll_service.update_payroll_record(
        payroll_id=payroll_id,
        update_data=request.model_dump(exclude_unset=True),
        updated_by=current_user.emp_id
    )
