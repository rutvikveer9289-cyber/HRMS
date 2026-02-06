
from app.core.database import engine, Base
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.file_upload import FileUploadLog
from app.models.leave import LeaveType, LeaveBalance, LeaveRequest, LeaveApprovalLog, Holiday
from app.models.salary_structure import SalaryStructure
from app.models.deduction import DeductionType, EmployeeDeduction
from app.models.payroll import PayrollRecord
from app.models.overtime import OvertimeRecord

print("Creating missing tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
