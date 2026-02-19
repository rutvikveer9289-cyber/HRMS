"""
Onboarding Endpoints (API v1)
Handles employee onboarding process
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil
from datetime import datetime

from app.api.dependencies import get_db, check_hr
from app.repositories.employee_repository import EmployeeRepository
from app.models.models import Employee, UserStatus, EmployeeDocument

router = APIRouter()

@router.get("/next-id")
def get_next_employee_id(
    hr: Employee = Depends(check_hr),
    db: Session = Depends(get_db)
):
    """
    Get next available employee ID
    """
    employees = db.query(Employee).filter(Employee.emp_id.like("RBIS%")).all()
    if not employees: return {"next_id": "RBIS0001"}
    
    max_num = 0
    for emp in employees:
        if emp.emp_id and emp.emp_id.startswith("RBIS"):
            try:
                num = int(emp.emp_id[4:])
                if num > max_num: max_num = num
            except ValueError: continue
            
    return {"next_id": f"RBIS{max_num + 1:04d}"}

@router.get("/pending")
def get_pending_onboarding(
    hr: Employee = Depends(check_hr),
    db: Session = Depends(get_db)
):
    """Get employees pending onboarding"""
    return db.query(Employee).filter(Employee.status == UserStatus.PENDING).all()

@router.post("/onboard")
async def onboard_employee(
    emp_id: str = Form(...),
    full_name: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(...),
    designation: str = Form(...),
    email: str = Form(...),
    id_proof: Optional[UploadFile] = File(None),
    address_proof: Optional[UploadFile] = File(None),
    education: Optional[UploadFile] = File(None),
    experience: Optional[UploadFile] = File(None),
    hr: Employee = Depends(check_hr),
    db: Session = Depends(get_db)
):
    """
    Complete employee onboarding with document support
    
    - Assigns emp_id and details
    - Changes status to ACTIVE
    - Saves uploaded documents to disk
    - Records document metadata in database
    """
    repo = EmployeeRepository(db)
    from app.utils.file_utils import normalize_emp_id
    
    normalized_id = normalize_emp_id(emp_id)
    target_email = email.lower()
    
    # Permission and conflict checks
    employee = repo.get_by_email(target_email)
    if employee and employee.status == UserStatus.ACTIVE:
         raise HTTPException(status_code=400, detail=f"Email {target_email} already active.")

    existing_id = repo.get_by_emp_id(normalized_id)
    if existing_id and (not employee or existing_id.id != employee.id):
        raise HTTPException(status_code=400, detail=f"ID {normalized_id} already taken.")

    if not employee:
        employee = Employee(email=target_email, emp_id=normalized_id, status=UserStatus.PENDING)
        db.add(employee)
        db.commit()
        db.refresh(employee)

    # Update basics
    employee.emp_id = normalized_id
    employee.full_name = full_name
    employee.first_name = first_name
    employee.last_name = last_name
    employee.phone_number = phone_number
    employee.designation = designation
    employee.status = UserStatus.ACTIVE
    
    # Process Documents
    doc_map = {
        "id_proof": id_proof,
        "address_proof": address_proof,
        "education": education,
        "experience": experience
    }
    
    upload_dir = os.path.join("uploads", "documents")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    for doc_type, file_obj in doc_map.items():
        if file_obj and file_obj.filename:
            # Generate safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{normalized_id}_{doc_type}_{timestamp}_{file_obj.filename}"
            file_path = os.path.join(upload_dir, filename)
            
            # Save to disk
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file_obj.file, buffer)
            
            # Record in DB
            new_doc = EmployeeDocument(
                emp_id=normalized_id,
                document_type=doc_type,
                document_name=file_obj.filename,
                file_name=filename,
                file_path=file_path
            )
            db.add(new_doc)

    db.commit()
    return {"message": "Onboarding completed with documents successfully"}
