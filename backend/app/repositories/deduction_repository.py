"""
Deduction Repository
Database access layer for Deduction models
"""
from sqlalchemy.orm import Session
from app.models.deduction import DeductionType, EmployeeDeduction
from typing import Optional, List
from datetime import date

class DeductionRepository:
    """Handles all database operations for Deduction models"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Deduction Type operations
    def get_deduction_type_by_id(self, id: int) -> Optional[DeductionType]:
        """Get deduction type by ID"""
        return self.db.query(DeductionType).filter(DeductionType.id == id).first()
    
    def get_deduction_type_by_name(self, name: str) -> Optional[DeductionType]:
        """Get deduction type by name"""
        return self.db.query(DeductionType).filter(DeductionType.name == name).first()
    
    def get_all_deduction_types(self, active_only: bool = True) -> List[DeductionType]:
        """Get all deduction types"""
        query = self.db.query(DeductionType)
        if active_only:
            query = query.filter(DeductionType.is_active == True)
        return query.all()
    
    def create_deduction_type(self, deduction_data: dict) -> DeductionType:
        """Create new deduction type"""
        deduction_type = DeductionType(**deduction_data)
        self.db.add(deduction_type)
        self.db.commit()
        self.db.refresh(deduction_type)
        return deduction_type
    
    def update_deduction_type(self, deduction_type: DeductionType) -> DeductionType:
        """Update deduction type"""
        self.db.commit()
        self.db.refresh(deduction_type)
        return deduction_type
    
    # Employee Deduction operations
    def get_employee_deduction_by_id(self, id: int) -> Optional[EmployeeDeduction]:
        """Get employee deduction by ID"""
        return self.db.query(EmployeeDeduction).filter(EmployeeDeduction.id == id).first()
    
    def get_active_deductions_by_emp_id(self, emp_id: str) -> List[EmployeeDeduction]:
        """
        Get all active deductions for an employee
        
        Args:
            emp_id: Employee ID
            
        Returns:
            List of active EmployeeDeduction objects
        """
        return self.db.query(EmployeeDeduction).filter(
            EmployeeDeduction.emp_id == emp_id,
            EmployeeDeduction.is_active == True
        ).all()
    
    def create_employee_deduction(self, deduction_data: dict) -> EmployeeDeduction:
        """Create new employee deduction"""
        emp_deduction = EmployeeDeduction(**deduction_data)
        self.db.add(emp_deduction)
        self.db.commit()
        self.db.refresh(emp_deduction)
        return emp_deduction
    
    def update_employee_deduction(self, emp_deduction: EmployeeDeduction) -> EmployeeDeduction:
        """Update employee deduction"""
        self.db.commit()
        self.db.refresh(emp_deduction)
        return emp_deduction
    
    def deactivate_employee_deduction(self, id: int, effective_to: date) -> None:
        """Deactivate an employee deduction"""
        self.db.query(EmployeeDeduction).filter(
            EmployeeDeduction.id == id
        ).update({
            "is_active": False,
            "effective_to": effective_to
        })
        self.db.commit()
    
    def delete_employee_deduction(self, emp_deduction: EmployeeDeduction) -> None:
        """Delete employee deduction"""
        self.db.delete(emp_deduction)
        self.db.commit()
