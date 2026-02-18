import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.attendance_service import AttendanceService
from app.models.employee import Employee

db = SessionLocal()
try:
    admin = db.query(Employee).filter(Employee.email == "superadmin@test.com").first()
    if not admin:
        print("Admin not found")
        sys.exit(1)
        
    file_path = r"d:\HRMS\rbis-hrms-main\files\EmployeeInOutDurationDailyAttendance RBIS.xls"
    with open(file_path, "rb") as f:
        content = f.read()
        
    class MockFile:
        def __init__(self, filename, content):
            self.filename = filename
            class MockF:
                def read(self, *args): return content
            self.file = MockF()
            self.content_type = "application/vnd.ms-excel"

    mock_file = MockFile("test_file.xls", content)
    
    service = AttendanceService(db)
    result = service.process_uploaded_files([mock_file], admin)
    print("\nResult:")
    print(result)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
