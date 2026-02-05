"""
Models Package
Exports all database models
"""
# Import Base and utilities
from app.models.base import Base, get_ist_now, IST

# Import Employee models
from app.models.employee import Employee, UserRole, UserStatus

# Import Attendance models
from app.models.attendance import Attendance

# Import File Upload models
from app.models.file_upload import FileUploadLog

# Import Leave models
from app.models.leave import (
    LeaveType,
    LeaveBalance,
    LeaveRequest,
    LeaveApprovalLog
)

# Import Salary models
from app.models.salary_structure import SalaryStructure

# Import Deduction models
from app.models.deduction import DeductionType, EmployeeDeduction, CalculationType

# Import Payroll models
from app.models.payroll import PayrollRecord, PayrollStatus

# Import Overtime models
from app.models.overtime import OvertimeRecord, OvertimeStatus

# Export all models and utilities
__all__ = [
    # Base
    "Base",
    "get_ist_now",
    "IST",
    
    # Employee
    "Employee",
    "UserRole",
    "UserStatus",
    
    # Attendance
    "Attendance",
    
    # File Upload
    "FileUploadLog",
    
    # Leave
    "LeaveType",
    "LeaveBalance",
    "LeaveRequest",
    "LeaveRequest",
    "LeaveApprovalLog",

    # Salary
    "SalaryStructure",

    # Deduction
    "DeductionType",
    "EmployeeDeduction",
    "CalculationType",

    # Payroll
    "PayrollRecord",
    "PayrollStatus",

    # Overtime
    "OvertimeRecord",
    "OvertimeStatus",
]
