"""
Salary Repository
Database access layer for Salary Structure model
"""
from sqlalchemy.orm import Session
from app.models.salary_structure import SalaryStructure
from typing import Optional, List
from datetime import date

class SalaryRepository:
    """Handles all database operations for Salary Structure model"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_by_emp_id(self, emp_id: str) -> Optional[SalaryStructure]:
        """
        Get active salary structure for an employee
        
        Args:
            emp_id: Employee ID
            
        Returns:
            Active SalaryStructure object or None
        """
        return self.db.query(SalaryStructure).filter(
            SalaryStructure.emp_id == emp_id,
            SalaryStructure.is_active == True
        ).first()
    
    def get_by_id(self, id: int) -> Optional[SalaryStructure]:
        """Get salary structure by ID"""
        return self.db.query(SalaryStructure).filter(SalaryStructure.id == id).first()
    
    def get_history_by_emp_id(self, emp_id: str) -> List[SalaryStructure]:
        """
        Get salary history for an employee
        
        Args:
            emp_id: Employee ID
            
        Returns:
            List of all SalaryStructure records for the employee
        """
        return self.db.query(SalaryStructure).filter(
            SalaryStructure.emp_id == emp_id
        ).order_by(SalaryStructure.effective_from.desc()).all()
    
    def create(self, salary_data: dict) -> SalaryStructure:
        """
        Create new salary structure
        
        Args:
            salary_data: Dictionary with salary fields
            
        Returns:
            Created SalaryStructure object
        """
        salary = SalaryStructure(**salary_data)
        self.db.add(salary)
        self.db.commit()
        self.db.refresh(salary)
        return salary
    
    def update(self, salary: SalaryStructure) -> SalaryStructure:
        """Update existing salary structure"""
        self.db.commit()
        self.db.refresh(salary)
        return salary
    
    def deactivate_previous(self, emp_id: str, effective_date: date) -> None:
        """
        Deactivate previous salary structures for an employee
        
        Args:
            emp_id: Employee ID
            effective_date: Date when new structure becomes effective
        """
        self.db.query(SalaryStructure).filter(
            SalaryStructure.emp_id == emp_id,
            SalaryStructure.is_active == True
        ).update({
            "is_active": False,
            "effective_to": effective_date
        })
        self.db.commit()
    
    def get_all_active(self) -> List[SalaryStructure]:
        """Get all active salary structures"""
        return self.db.query(SalaryStructure).filter(
            SalaryStructure.is_active == True
        ).all()
