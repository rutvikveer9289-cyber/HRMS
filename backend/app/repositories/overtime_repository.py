"""
Overtime Repository
Database access layer for Overtime Record model
"""
from sqlalchemy.orm import Session
from app.models.overtime import OvertimeRecord
from typing import Optional, List
from datetime import date
from decimal import Decimal

class OvertimeRepository:
    """Handles all database operations for Overtime Record model"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[OvertimeRecord]:
        """Get overtime record by ID"""
        return self.db.query(OvertimeRecord).filter(OvertimeRecord.id == id).first()
    
    def get_by_emp_date(self, emp_id: str, date_val: date) -> Optional[OvertimeRecord]:
        """
        Get overtime record for specific employee and date
        
        Args:
            emp_id: Employee ID
            date_val: Date
            
        Returns:
            OvertimeRecord object or None
        """
        return self.db.query(OvertimeRecord).filter(
            OvertimeRecord.emp_id == emp_id,
            OvertimeRecord.date == date_val
        ).first()
    
    def get_by_emp_date_range(self, emp_id: str, start_date: date, end_date: date) -> List[OvertimeRecord]:
        """
        Get overtime records for employee within date range
        
        Args:
            emp_id: Employee ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of OvertimeRecord objects
        """
        return self.db.query(OvertimeRecord).filter(
            OvertimeRecord.emp_id == emp_id,
            OvertimeRecord.date >= start_date,
            OvertimeRecord.date <= end_date
        ).order_by(OvertimeRecord.date).all()
    
    def get_by_status(self, status: str) -> List[OvertimeRecord]:
        """Get overtime records by status"""
        return self.db.query(OvertimeRecord).filter(
            OvertimeRecord.status == status
        ).all()
    
    def get_pending_approvals(self) -> List[OvertimeRecord]:
        """Get all pending overtime approvals"""
        return self.db.query(OvertimeRecord).filter(
            OvertimeRecord.status == "PENDING"
        ).order_by(OvertimeRecord.date.desc()).all()
    
    def create(self, overtime_data: dict) -> OvertimeRecord:
        """
        Create new overtime record
        
        Args:
            overtime_data: Dictionary with overtime fields
            
        Returns:
            Created OvertimeRecord object
        """
        overtime = OvertimeRecord(**overtime_data)
        self.db.add(overtime)
        self.db.commit()
        self.db.refresh(overtime)
        return overtime
    
    def update(self, overtime: OvertimeRecord) -> OvertimeRecord:
        """Update existing overtime record"""
        self.db.commit()
        self.db.refresh(overtime)
        return overtime
    
    def delete(self, overtime: OvertimeRecord) -> None:
        """Delete overtime record"""
        self.db.delete(overtime)
        self.db.commit()
    
    def get_total_overtime_hours(self, emp_id: str, start_date: date, end_date: date) -> Decimal:
        """
        Calculate total overtime hours for employee in date range
        
        Args:
            emp_id: Employee ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Total overtime hours as Decimal
        """
        from sqlalchemy import func
        result = self.db.query(func.sum(OvertimeRecord.overtime_hours)).filter(
            OvertimeRecord.emp_id == emp_id,
            OvertimeRecord.date >= start_date,
            OvertimeRecord.date <= end_date,
            OvertimeRecord.status == "APPROVED"
        ).scalar()
        
        return result if result else Decimal('0.00')
    
    def get_total_overtime_amount(self, emp_id: str, start_date: date, end_date: date) -> Decimal:
        """
        Calculate total overtime amount for employee in date range
        
        Args:
            emp_id: Employee ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Total overtime amount as Decimal
        """
        from sqlalchemy import func
        result = self.db.query(func.sum(OvertimeRecord.overtime_amount)).filter(
            OvertimeRecord.emp_id == emp_id,
            OvertimeRecord.date >= start_date,
            OvertimeRecord.date <= end_date,
            OvertimeRecord.status == "APPROVED"
        ).scalar()
        
        return result if result else Decimal('0.00')
