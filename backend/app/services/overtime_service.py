"""
Overtime Service
Business logic for overtime calculation and management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.overtime_repository import OvertimeRepository
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.salary_repository import SalaryRepository
from decimal import Decimal
from datetime import date, datetime, timedelta

class OvertimeService:
    """Handles overtime calculation business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.overtime_repo = OvertimeRepository(db)
        self.attendance_repo = AttendanceRepository(db)
        self.salary_repo = SalaryRepository(db)
    
    def calculate_overtime_from_attendance(self, emp_id: str, start_date: date, end_date: date, overtime_rate: float = 1.5) -> list:
        """
        Calculate overtime from attendance records
        
        Args:
            emp_id: Employee ID
            start_date: Start date
            end_date: End date
            overtime_rate: Overtime multiplier (default 1.5x)
            
        Returns:
            List of created overtime records
        """
        # Get attendance records
        attendance_records = self.attendance_repo.get_by_emp_date_range(emp_id, start_date, end_date)
        
        if not attendance_records:
            raise HTTPException(status_code=404, detail="No attendance records found for the period")
        
        # Get employee salary for hourly rate calculation
        salary = self.salary_repo.get_active_by_emp_id(emp_id)
        if not salary:
            raise HTTPException(status_code=404, detail="No active salary structure found")
        
        # Calculate hourly rate (assuming 8 hours/day, ~22 working days/month)
        hourly_rate = salary.basic_salary / Decimal('176')  # 22 days * 8 hours
        
        overtime_records = []
        regular_hours = Decimal('8.00')
        
        for attendance in attendance_records:
            # Parse total duration to get actual hours
            actual_hours = self._parse_duration_to_hours(attendance.total_duration)
            
            if actual_hours > regular_hours:
                overtime_hours = actual_hours - regular_hours
                overtime_amount = overtime_hours * hourly_rate * Decimal(str(overtime_rate))
                
                # Check if overtime record already exists
                existing = self.overtime_repo.get_by_emp_date(emp_id, attendance.date)
                if not existing:
                    overtime_data = {
                        "emp_id": emp_id,
                        "date": attendance.date,
                        "regular_hours": regular_hours,
                        "actual_hours": actual_hours,
                        "overtime_hours": overtime_hours,
                        "overtime_rate": Decimal(str(overtime_rate)),
                        "overtime_amount": overtime_amount,
                        "status": "PENDING"
                    }
                    overtime_record = self.overtime_repo.create(overtime_data)
                    overtime_records.append(overtime_record)
        
        return overtime_records
    
    def approve_overtime(self, overtime_id: int, approved_by: str, remarks: str = None):
        """Approve overtime record"""
        overtime = self.overtime_repo.get_by_id(overtime_id)
        if not overtime:
            raise HTTPException(status_code=404, detail="Overtime record not found")
        
        overtime.status = "APPROVED"
        overtime.approved_by = approved_by
        overtime.approved_at = datetime.now()
        if remarks:
            overtime.remarks = remarks
        
        return self.overtime_repo.update(overtime)
    
    def reject_overtime(self, overtime_id: int, approved_by: str, remarks: str):
        """Reject overtime record"""
        overtime = self.overtime_repo.get_by_id(overtime_id)
        if not overtime:
            raise HTTPException(status_code=404, detail="Overtime record not found")
        
        overtime.status = "REJECTED"
        overtime.approved_by = approved_by
        overtime.approved_at = datetime.now()
        overtime.remarks = remarks
        
        return self.overtime_repo.update(overtime)
    
    def get_overtime_summary(self, emp_id: str, month: int, year: int) -> dict:
        """Get overtime summary for a month"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        total_hours = self.overtime_repo.get_total_overtime_hours(emp_id, start_date, end_date)
        total_amount = self.overtime_repo.get_total_overtime_amount(emp_id, start_date, end_date)
        
        return {
            "emp_id": emp_id,
            "month": month,
            "year": year,
            "total_overtime_hours": float(total_hours),
            "total_overtime_amount": float(total_amount)
        }
    
    def _parse_duration_to_hours(self, duration_str: str) -> Decimal:
        """
        Parse duration string to hours
        Example: "09:30:00" -> 9.5 hours
        """
        if not duration_str:
            return Decimal('0.00')
        
        try:
            parts = duration_str.split(':')
            hours = Decimal(parts[0])
            minutes = Decimal(parts[1]) / Decimal('60')
            return hours + minutes
        except:
            return Decimal('0.00')
