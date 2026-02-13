"""
Models Module (Deprecated)
This file is kept for backward compatibility. 
It re-exports models from their respective modular files.
"""

# Re-export Base
from app.core.database import Base
# Re-export utilities
from app.models.base import get_ist_now, IST

# Re-export Employee models
from app.models.employee import Employee, UserRole, UserStatus

# Re-export Attendance
from app.models.attendance import Attendance

# Re-export File Upload
from app.models.file_upload import FileUploadLog

# Re-export Leave models
from app.models.leave import (
    LeaveType,
    LeaveBalance,
    LeaveRequest,
    LeaveApprovalLog,
    Holiday
)

# Re-export Communication models
from app.models.communication import Announcement, Notification

# Re-export Payroll & Salary models
from app.models.salary_structure import SalaryStructure
from app.models.deduction import DeductionType, EmployeeDeduction, CalculationType
from app.models.payroll import PayrollRecord, PayrollStatus
from app.models.overtime import OvertimeRecord, OvertimeStatus
