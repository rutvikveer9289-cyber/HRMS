"""
Admin Endpoints (API v1)
Handles employee management operations
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.api.dependencies import get_db, check_admin
from app.services.admin_service import AdminService
from app.models.models import Employee

router = APIRouter()

class EmployeeUpdate(BaseModel):
    """Schema for employee update"""
    full_name: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_no: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None

@router.get("/employees")
async def get_employees(
    admin: Employee = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """
    Get all employees
    
    - Returns list of all employees
    - Requires admin/HR/CEO role
    """
    service = AdminService(db)
    return service.get_all_employees()

@router.put("/employees/{id}")
async def update_employee(
    id: int,
    emp_data: EmployeeUpdate,
    admin: Employee = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """
    Update employee details
    
    - Updates employee information
    - HR cannot edit (CEO/Admin only)
    - Checks for conflicts
    """
    service = AdminService(db)
    update_dict = emp_data.dict(exclude_unset=True)
    return service.update_employee(id, update_dict, admin)

@router.delete("/employees/{id}")
async def delete_employee(
    id: int,
    admin: Employee = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """
    Delete employee
    
    - Deletes employee from system
    - HR cannot delete (CEO/Admin only)
    """
    service = AdminService(db)
    return service.delete_employee(id, admin)

@router.get("/employees/template")
async def download_master_template(
    admin: Employee = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Download employee master Excel template"""
    from fastapi.responses import Response
    service = AdminService(db)
    template_bytes = service.generate_master_template()
    return Response(
        content=template_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Employee_Master_Template.xlsx"}
    )

@router.post("/employees/upload")
async def upload_master(
    file: UploadFile = File(...),
    admin: Employee = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Upload completed employee master Excel"""
    service = AdminService(db)
    return await service.process_employee_master(file, admin)

# --- Employee Document Management ---

@router.get("/employees/{emp_id}/documents")
async def get_employee_documents(
    emp_id: str,
    admin: Employee = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Get all documents for a specific employee"""
    from app.models.models import EmployeeDocument
    docs = db.query(EmployeeDocument).filter(EmployeeDocument.emp_id == emp_id).all()
    return docs

@router.post("/employees/{emp_id}/documents/upload")
async def upload_employee_document(
    emp_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    admin: Employee = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Upload a new document for an existing employee"""
    import os
    import shutil
    from datetime import datetime
    from app.models.models import EmployeeDocument
    
    upload_dir = os.path.join("uploads", "documents")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    # Generate safe filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{emp_id}_{document_type}_{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Record in DB
    new_doc = EmployeeDocument(
        emp_id=emp_id,
        document_type=document_type,
        document_name=file.filename,
        file_name=filename,
        file_path=file_path
    )
    db.add(new_doc)
    db.commit()
    return {"message": "Document uploaded successfully", "document": new_doc}

@router.delete("/employees/documents/{doc_id}")
async def delete_employee_document(
    doc_id: int,
    admin: Employee = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Delete a specific employee document"""
    import os
    from app.models.models import EmployeeDocument
    
    doc = db.query(EmployeeDocument).filter(EmployeeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Delete from disk if exists
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
        
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}
