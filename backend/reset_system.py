import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models.employee import Employee, UserRole, UserStatus
from app.core.security import get_password_hash
from app.models.attendance import Attendance
from app.models.file_upload import FileUploadLog
from app.models.leave import LeaveType, LeaveBalance, LeaveRequest, LeaveApprovalLog, Holiday
from app.models.salary_structure import SalaryStructure
from app.models.deduction import DeductionType, EmployeeDeduction
from app.models.payroll import PayrollRecord
# from app.models.overtime import OvertimeRecord - Removed
from app.models.communication import Announcement, Notification

def reset_and_seed():
    db = SessionLocal()
    try:
        print("Stopping any active connections (if possible)...")
        
        print("Dropping all existing tables...")
        from sqlalchemy import text
        # Explicitly drop tables that might not be in metadata anymore (like Overtime)
        try:
            db.execute(text("DROP TABLE IF EXISTS overtime_records"))
            db.execute(text("DROP TABLE IF EXISTS overtime_approvals"))
            db.execute(text("DROP TABLE IF EXISTS payroll_records")) # Just in case
            db.commit()
        except Exception as ignored:
            print(f"Warning during pre-drop: {ignored}")

        Base.metadata.drop_all(bind=engine)
        
        print("Recreating tables from fresh schemas...")
        Base.metadata.create_all(bind=engine)
        
        print("Seeding administrative users...")
        admin_users = [
            {
                "email": "superadmin@test.com",
                "password": "Test@123",
                "full_name": "Super Admin",
                "role": UserRole.SUPER_ADMIN,
                "emp_id": "ADMIN001",
                "designation": "System Administrator"
            },
            {
                "email": "ceo@test.com",
                "password": "Test@123",
                "full_name": "CEO User",
                "role": UserRole.CEO,
                "emp_id": "RBIS-CEO1",
                "designation": "Chief Executive Officer"
            },
            {
                "email": "hr@test.com",
                "password": "Test@123",
                "full_name": "HR Manager",
                "role": UserRole.HR,
                "emp_id": "RBIS-HR01",
                "designation": "Human Resources"
            }
        ]
        
        for u_data in admin_users:
            new_user = Employee(
                email=u_data["email"],
                password_hash=get_password_hash(u_data["password"]),
                full_name=u_data["full_name"],
                role=u_data["role"],
                emp_id=u_data["emp_id"],
                designation=u_data["designation"],
                is_verified=True,
                status=UserStatus.ACTIVE
            )
            db.add(new_user)
        
        # Import from Excel if exists
        excel_path = r"d:\HRMS\rbis-hrms-main\files\Employee_Details.xlsx"
        if os.path.exists(excel_path):
            import pandas as pd
            print(f"Importing employees from {excel_path}...")
            df = pd.read_excel(excel_path)
            
            # Map columns
            # ['Name', 'Phone Number', 'First Name', 'Last Name', 'Designation', 'EmpId', 'Email']
            for _, row in df.iterrows():
                emp_email = str(row.get('Email', '')).strip()
                if not emp_email or '@' not in emp_email:
                    continue
                
                # Check if already added (like admin)
                if any(u['email'] == emp_email for u in admin_users):
                    continue

                from app.utils.file_utils import normalize_emp_id
                emp = Employee(
                    email=emp_email,
                    password_hash=get_password_hash("Rbis@123"),
                    full_name=str(row.get('Name', '')),
                    first_name=str(row.get('First Name', '')),
                    last_name=str(row.get('Last Name', '')),
                    phone_number=str(row.get('Phone Number', '')),
                    role=UserRole.EMPLOYEE,
                    emp_id=normalize_emp_id(str(row.get('EmpId', ''))),
                    designation=str(row.get('Designation', '')),
                    is_verified=True,
                    status=UserStatus.ACTIVE
                )
                db.add(emp)
            print(f"Successfully imported {len(df)} employees from Excel.")
        else:
            print("No Employee_Details.xlsx found, skipping bulk import.")
        
        # Seed leave types
        print("Seeding leave types...")
        leave_types = [
            {"name": "Paid Leave", "annual_quota": 20, "allow_carry_forward": False},
        ]
        
        for lt in leave_types:
            leave_type = LeaveType(
                name=lt["name"],
                annual_quota=lt["annual_quota"],
                is_paid=True,  # All leaves are paid
                allow_carry_forward=lt["allow_carry_forward"],
                is_active=True
            )
            db.add(leave_type)
        
        db.flush() # Ensure IDs are generated
        print(f"Successfully seeded {len(leave_types)} leave types.")
        
        # Seed holidays for 2026
        print("Seeding holidays for 2026...")
        holidays_2026 = [
            {"name": "New Year's Day", "date": "2026-01-01", "day": "Thursday"},
            {"name": "Republic Day", "date": "2026-01-26", "day": "Monday"},
            {"name": "Holi", "date": "2026-03-14", "day": "Saturday"},
            {"name": "Good Friday", "date": "2026-04-03", "day": "Friday"},
            {"name": "Eid al-Fitr", "date": "2026-04-21", "day": "Tuesday"},
            {"name": "Independence Day", "date": "2026-08-15", "day": "Saturday"},
            {"name": "Janmashtami", "date": "2026-09-04", "day": "Friday"},
            {"name": "Gandhi Jayanti", "date": "2026-10-02", "day": "Friday"},
            {"name": "Dussehra", "date": "2026-10-22", "day": "Thursday"},
            {"name": "Diwali", "date": "2026-11-08", "day": "Sunday"},
            {"name": "Christmas", "date": "2026-12-25", "day": "Friday"}
        ]
        
        for h in holidays_2026:
            holiday_date = datetime.strptime(h["date"], "%Y-%m-%d").date()
            holiday = Holiday(
                name=h["name"],
                date=holiday_date,
                year=holiday_date.year,
                day=h["day"]
            )
            db.add(holiday)
        
        print(f"Successfully seeded {len(holidays_2026)} holidays.")
        
        # Seed leave balances for all employees
        print("Seeding leave balances for 2026...")
        all_employees = db.query(Employee).all()
        # Retrieve freshly created leave types from DB
        db_leave_types = db.query(LeaveType).all()
        
        current_year = 2026
        balance_count = 0
        
        for emp in all_employees:
            # Skip if balances already exist (though specific logic here assumes fresh DB)
            existing = db.query(LeaveBalance).filter_by(emp_id=emp.emp_id, year=current_year).first()
            if existing:
                continue

            for lt in db_leave_types:
                balance = LeaveBalance(
                    emp_id=emp.emp_id,
                    leave_type_id=lt.id,
                    year=current_year,
                    allocated=lt.annual_quota,
                    used=0
                )
                db.add(balance)
                balance_count += 1
        
        print(f"Successfully seeded {balance_count} leave balance records.")
        
        db.commit()
        print("\nSUCCESS: Application has been reset to a fresh state with your data.")
        print("-" * 40)
        print("Login Credentials:")
        print("Email: superadmin@rbistech.com")
        print("Password: Rbis@123")
        print("-" * 40)
        
    except Exception as e:
        print(f"FAILED to reset: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()
