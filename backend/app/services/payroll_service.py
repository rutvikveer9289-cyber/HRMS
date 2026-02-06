"""
Payroll Service
Business logic for payroll processing and calculations
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.payroll_repository import PayrollRepository
from app.repositories.salary_repository import SalaryRepository
from app.repositories.deduction_repository import DeductionRepository
from app.repositories.overtime_repository import OvertimeRepository
from app.repositories.attendance_repository import AttendanceRepository
from decimal import Decimal
from datetime import date, timedelta
import json
import calendar

class PayrollService:
    """Handles payroll processing business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.payroll_repo = PayrollRepository(db)
        self.salary_repo = SalaryRepository(db)
        self.deduction_repo = DeductionRepository(db)
        self.overtime_repo = OvertimeRepository(db)
        self.attendance_repo = AttendanceRepository(db)
    
    def process_payroll(self, emp_id: str, month: int, year: int, processed_by: str) -> dict:
        """
        Process monthly payroll for an employee
        
        Args:
            emp_id: Employee ID
            month: Month (1-12)
            year: Year
            processed_by: User processing the payroll
            
        Returns:
            Processed payroll record
        """
        # Normalize emp_id to uppercase
        emp_id = emp_id.upper()
        
        # Check if payroll already exists
        existing = self.payroll_repo.get_by_emp_month_year(emp_id, month, year)
        if existing:
            raise HTTPException(status_code=400, detail="Payroll already processed for this month")
        
        # Get salary structure
        salary = self.salary_repo.get_active_by_emp_id(emp_id)
        if not salary:
            raise HTTPException(status_code=404, detail="No active salary structure found")
        
        # Calculate working days and attendance
        working_days = self._get_working_days(month, year)
        attendance_data = self._get_attendance_summary(emp_id, month, year)
        
        # Get overtime
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        overtime_amount = self.overtime_repo.get_total_overtime_amount(emp_id, start_date, end_date)
        overtime_hours = self.overtime_repo.get_total_overtime_hours(emp_id, start_date, end_date)
        
        # Calculate deductions
        deductions = self._calculate_deductions(emp_id, salary)
        total_deductions = sum(d['amount'] for d in deductions)
        
        # Calculate net salary
        gross_salary = salary.gross_salary
        net_salary = gross_salary + overtime_amount - Decimal(str(total_deductions))
        
        # Create payroll record
        payroll_data = {
            "emp_id": emp_id,
            "month": month,
            "year": year,
            "basic_salary": salary.basic_salary,
            "hra": salary.hra,
            "transport_allowance": salary.transport_allowance,
            "dearness_allowance": salary.dearness_allowance,
            "medical_allowance": salary.medical_allowance,
            "special_allowance": salary.special_allowance,
            "other_allowances": salary.other_allowances,
            "overtime_amount": overtime_amount,
            "gross_salary": gross_salary,
            "total_deductions": Decimal(str(total_deductions)),
            "net_salary": net_salary,
            "deduction_details": json.dumps(deductions),
            "working_days": working_days,
            "present_days": attendance_data['present_days'],
            "absent_days": attendance_data['absent_days'],
            "overtime_hours": overtime_hours,
            "status": "PROCESSED",
            "processed_by": processed_by
        }
        
        return self.payroll_repo.create(payroll_data)
    
    def get_payroll_record(self, emp_id: str, month: int, year: int):
        """Get payroll record for employee"""
        payroll = self.payroll_repo.get_by_emp_month_year(emp_id, month, year)
        if not payroll:
            raise HTTPException(status_code=404, detail="Payroll record not found")
        return payroll
    
    def update_payment_status(self, payroll_id: int, status: str, payment_date: date = None, payment_method: str = None):
        """Update payroll payment status"""
        payroll = self.payroll_repo.get_by_id(payroll_id)
        if not payroll:
            raise HTTPException(status_code=404, detail="Payroll record not found")
        
        payroll.status = status
        if payment_date:
            payroll.payment_date = payment_date
        if payment_method:
            payroll.payment_method = payment_method
        
        return self.payroll_repo.update(payroll)
    
    def get_payroll_list(self, month: int = None, year: int = None, status: str = None):
        """Get list of payroll records with filters"""
        if month and year:
            return self.payroll_repo.get_by_month_year(month, year)
        elif status:
            return self.payroll_repo.get_by_status(status)
        else:
            raise HTTPException(status_code=400, detail="Please provide month/year or status filter")
    
    def _calculate_deductions(self, emp_id: str, salary) -> list:
        """Calculate all deductions for employee"""
        deductions = []
        employee_deductions = self.deduction_repo.get_active_deductions_by_emp_id(emp_id)
        
        for emp_ded in employee_deductions:
            deduction_type = self.deduction_repo.get_deduction_type_by_id(emp_ded.deduction_type_id)
            if not deduction_type:
                continue
            
            if emp_ded.calculation_type == "PERCENTAGE":
                # Calculate percentage of basic salary
                amount = (salary.basic_salary * emp_ded.value) / Decimal('100')
            else:  # FIXED
                amount = emp_ded.value
            
            deductions.append({
                "name": deduction_type.name,
                "type": emp_ded.calculation_type,
                "value": float(emp_ded.value),
                "amount": float(amount)
            })
        
        return deductions
    
    def _get_working_days(self, month: int, year: int) -> int:
        """Calculate working days in a month (excluding Sundays)"""
        _, num_days = calendar.monthrange(year, month)
        working_days = 0
        
        for day in range(1, num_days + 1):
            day_of_week = date(year, month, day).weekday()
            if day_of_week != 6:  # 6 is Sunday
                working_days += 1
        
        return working_days
    
    def _get_attendance_summary(self, emp_id: str, month: int, year: int) -> dict:
        """Get attendance summary for the month"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        attendance_records = self.attendance_repo.get_by_emp_date_range(emp_id, start_date, end_date)
        
        present_days = len([a for a in attendance_records if a.attendance_status == "Present"])
        working_days = self._get_working_days(month, year)
        absent_days = working_days - present_days
        
        return {
            "present_days": present_days,
            "absent_days": absent_days,
            "working_days": working_days
        }
