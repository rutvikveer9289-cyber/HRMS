
from app.core.database import engine, Base, DATABASE_URL
import os
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.file_upload import FileUploadLog
from app.models.leave import LeaveType, LeaveBalance, LeaveRequest, LeaveApprovalLog, Holiday
from app.models.salary_structure import SalaryStructure
from app.models.deduction import DeductionType, EmployeeDeduction
from app.models.payroll import PayrollRecord
from app.models.overtime import OvertimeRecord

print(f"DATABASE_URL: {DATABASE_URL}")
print(f"Working Directory: {os.getcwd()}")
print("Creating missing tables...")
Base.metadata.create_all(bind=engine)
print("Done.")

import sqlite3
db_path = "hrms.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in current hrms.db:", tables)
    conn.close()
