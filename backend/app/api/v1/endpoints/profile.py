"""
Profile Endpoints (API v1)
Handles user profile operations
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.api.dependencies import get_db, get_current_user
from app.repositories.employee_repository import EmployeeRepository
from app.models.models import Employee

router = APIRouter()

class ProfileUpdate(BaseModel):
    """Schema for profile update - restricted to non-core fields"""
    phone_number: Optional[str] = None
    designation: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_no: Optional[str] = None
    bank_ifsc_code: Optional[str] = None

@router.get("/me")
@router.get("")  # Alias for /profile/
async def get_my_profile(
    user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile
    
    - Returns authenticated user's profile
    """
    return {
        "emp_id": user.emp_id,
        "full_name": user.full_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "designation": user.designation,
        "role": user.role,
        "status": user.status,
        "department": user.department,
        "location": user.location,
        "bank_name": user.bank_name,
        "bank_account_no": user.bank_account_no,
        "bank_ifsc_code": user.bank_ifsc_code
    }

@router.put("/me")
async def update_my_profile(
    data: ProfileUpdate,
    user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    
    - Updates user's own profile
    - Limited fields (no role/status change)
    """
    try:
        repo = EmployeeRepository(db)
        
        # Merge user into current session to avoid detached instance error
        user = db.merge(user)
        
        # Use model_dump for Pydantic v2 compatibility
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        repo.update(user)
        return {"message": "Profile updated successfully"}
    except Exception as e:
        from fastapi import HTTPException
        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

