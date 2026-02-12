"""
Payroll Repository
Database access layer for Payroll Record model
"""
from sqlalchemy.orm import Session, joinedload
from app.models.payroll import PayrollRecord
from typing import Optional, List

class PayrollRepository:
    """Handles all database operations for Payroll Record model"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[PayrollRecord]:
        """Get all payroll records"""
        return self.db.query(PayrollRecord).options(joinedload(PayrollRecord.owner)).order_by(
            PayrollRecord.year.desc(), 
            PayrollRecord.month.desc()
        ).all()
    
    def get_by_id(self, id: int) -> Optional[PayrollRecord]:
        """Get payroll record by ID"""
        return self.db.query(PayrollRecord).options(joinedload(PayrollRecord.owner)).filter(PayrollRecord.id == id).first()
    
    def get_by_emp_month_year(self, emp_id: str, month: int, year: int) -> Optional[PayrollRecord]:
        """
        Get payroll record for specific employee, month, and year
        
        Args:
            emp_id: Employee ID
            month: Month (1-12)
            year: Year
            
        Returns:
            PayrollRecord object or None
        """
        return self.db.query(PayrollRecord).options(joinedload(PayrollRecord.owner)).filter(
            PayrollRecord.emp_id == emp_id,
            PayrollRecord.month == month,
            PayrollRecord.year == year
        ).first()
    
    def get_by_emp_id(self, emp_id: str, limit: int = None) -> List[PayrollRecord]:
        """
        Get payroll history for an employee
        
        Args:
            emp_id: Employee ID
            limit: Optional limit on number of records
            
        Returns:
            List of PayrollRecord objects
        """
        query = self.db.query(PayrollRecord).options(joinedload(PayrollRecord.owner)).filter(
            PayrollRecord.emp_id == emp_id
        ).order_by(PayrollRecord.year.desc(), PayrollRecord.month.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_by_month_year(self, month: int, year: int) -> List[PayrollRecord]:
        """
        Get all payroll records for a specific month and year
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            List of PayrollRecord objects
        """
        return self.db.query(PayrollRecord).options(joinedload(PayrollRecord.owner)).filter(
            PayrollRecord.month == month,
            PayrollRecord.year == year
        ).all()
    
    def get_by_status(self, status: str) -> List[PayrollRecord]:
        """Get payroll records by status"""
        return self.db.query(PayrollRecord).filter(
            PayrollRecord.status == status
        ).all()
    
    def create(self, payroll_data: dict) -> PayrollRecord:
        """
        Create new payroll record
        
        Args:
            payroll_data: Dictionary with payroll fields
            
        Returns:
            Created PayrollRecord object
        """
        payroll = PayrollRecord(**payroll_data)
        self.db.add(payroll)
        self.db.commit()
        self.db.refresh(payroll)
        return payroll
    
    def update(self, payroll: PayrollRecord) -> PayrollRecord:
        """Update existing payroll record"""
        self.db.commit()
        self.db.refresh(payroll)
        return payroll
    
    def delete(self, payroll: PayrollRecord) -> None:
        """Delete payroll record"""
        self.db.delete(payroll)
        self.db.commit()
    
    def exists(self, emp_id: str, month: int, year: int) -> bool:
        """Check if payroll record exists"""
        return self.db.query(PayrollRecord).filter(
            PayrollRecord.emp_id == emp_id,
            PayrollRecord.month == month,
            PayrollRecord.year == year
        ).first() is not None
