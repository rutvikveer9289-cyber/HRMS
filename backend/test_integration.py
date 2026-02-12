import sys
import os
from datetime import date, timedelta
from decimal import Decimal

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.leave_service import LeaveService
from app.services.payroll_service import PayrollService
from app.models.employee import Employee
from app.models.leave import LeaveType, LeaveRequest, Holiday
from app.models.attendance import Attendance

def setup_test_data(db):
    """Setup basic test data"""
    # Create test employee
    emp_id = "RBIS9999"
    emp = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if not emp:
        emp = Employee(
            emp_id=emp_id, 
            full_name="Integration Tester", 
            email="tester@rbistech.com", 
            role="SUPER_ADMIN",
            status="ACTIVE"
        )
        db.add(emp)
    
    # Create leave type
    type_name = "integration_sick_leave"
    l_type = db.query(LeaveType).filter(LeaveType.name == type_name).first()
    if not l_type:
        l_type = LeaveType(name=type_name, annual_quota=10, is_paid=True)
        db.add(l_type)
    
    db.commit()
    db.refresh(emp)
    db.refresh(l_type)
    return emp, l_type

def test_holiday_exclusion():
    """Verify that holidays are excluded from leave days calculation"""
    db = SessionLocal()
    try:
        service = LeaveService(db)
        emp, l_type = setup_test_data(db)
        
        # Define a range: Next Monday to Wednesday (3 days)
        # Find next Monday
        today = date.today()
        monday = today + timedelta(days=(7 - today.weekday()))
        wednesday = monday + timedelta(days=2)
        
        # Add a holiday on Tuesday
        tuesday = monday + timedelta(days=1)
        holiday_name = "Test Integration Holiday"
        existing_holiday = db.query(Holiday).filter(Holiday.date == tuesday).first()
        if not existing_holiday:
            db.add(Holiday(name=holiday_name, date=tuesday, year=tuesday.year))
            db.commit()
            
        # Calculate work days
        days = service._calculate_work_days(monday, wednesday)
        
        print(f"[TEST] Holiday Exclusion: {monday} to {wednesday} (Should be 2 days, holiday on {tuesday})")
        print(f"  > Calculated Days: {days}")
        
        assert days == 2, f"Expected 2 days, but got {days}"
        print("  > [PASS] Holiday correctly excluded.")
        
    finally:
        db.close()

def test_payroll_attendance_summary():
    """Verify that Present, Half Day, Absent, and On Leave are correctly counted in payroll"""
    db = SessionLocal()
    try:
        service = PayrollService(db)
        emp, _ = setup_test_data(db)
        emp_id = emp.emp_id
        
        month = 1
        year = 2026
        
        # Clean existing attendance for this month
        db.query(Attendance).filter(
            Attendance.emp_id == emp_id,
            Attendance.date >= date(year, month, 1),
            Attendance.date <= date(year, month, 31)
        ).delete()
        db.commit()
        
        # Add varied attendance
        # 10 Present
        for d in range(1, 11):
            db.add(Attendance(emp_id=emp_id, date=date(year, month, d), attendance_status="Present"))
        
        # 2 Half Day
        for d in range(11, 13):
            db.add(Attendance(emp_id=emp_id, date=date(year, month, d), attendance_status="Half Day"))
            
        # 2 On Leave
        for d in range(13, 15):
            db.add(Attendance(emp_id=emp_id, date=date(year, month, d), attendance_status="On Leave"))
            
        db.commit()
        
        # Working days in Jan 2026 (excluding Sundays)
        # Jan 1 2026 is Thursday. 31 days.
        # Sundays: 4, 11, 18, 25. (4 total)
        # Total working = 31 - 4 = 27.
        
        summary = service._get_attendance_summary(emp_id, month, year)
        
        print(f"[TEST] Payroll Attendance Summary (Jan 2026):")
        print(f"  > Working Days (Manual): 27")
        print(f"  > Working Days (Code): {summary['working_days']}")
        print(f"  > Present (Full): 10, Half: 2 -> Effective Present: {summary['present_days']}")
        print(f"  > On Leave: 2 -> Status: {summary['on_leave_days']}")
        print(f"  > Absent: {summary['absent_days']} (Should be 27 - 11 - 2 = 14)")
        
        assert summary['working_days'] == 27
        assert summary['present_days'] == 11.0 # 10 + 2*0.5
        assert summary['on_leave_days'] == 2
        assert summary['absent_days'] == 14.0 # 27 - 11 - 2
        
        print("  > [PASS] Payroll attendance summary correctly calculated.")
        
    finally:
        db.close()

def test_onboarding():
    """Verify employee onboarding flow"""
    db = SessionLocal()
    try:
        from app.api.v1.endpoints.onboarding import OnboardingData, complete_onboarding
        from app.models.employee import UserStatus
        
        emp_email = "new_hire@rbistech.com"
        # Clean up
        db.query(Employee).filter(Employee.email == emp_email).delete()
        db.commit()
        
        # 1. Start with a pending employee
        new_emp = Employee(
            email=emp_email,
            status=UserStatus.PENDING,
            role="EMPLOYEE"
        )
        db.add(new_emp)
        db.commit()
        
        # 2. Run onboarding
        data = OnboardingData(
            emp_id="RBIS9001",
            full_name="New Hire",
            first_name="New",
            last_name="Hire",
            phone_number="1234567890",
            designation="Software Engineer",
            email=emp_email
        )
        
        # Create a mock HR user
        hr_user = Employee(role="HR", emp_id="HR001")
        
        print(f"[TEST] Onboarding Flow for {emp_email}...")
        result = complete_onboarding(data=data, email=emp_email, hr=hr_user, db=db)
        
        print(f"  > Result: {result}")
        
        # 3. Verify status
        db.refresh(new_emp)
        assert new_emp.status == UserStatus.ACTIVE
        assert new_emp.emp_id == "RBIS9001"
        assert new_emp.designation == "Software Engineer"
        
        print("  > [PASS] Onboarding flow successful.")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Running Integration Tests...")
    test_holiday_exclusion()
    test_payroll_attendance_summary()
    test_onboarding()
    print("All Integration Tests Passed!")
