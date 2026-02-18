import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.repositories.employee_repository import EmployeeRepository
from app.utils.file_utils import normalize_emp_id

db = SessionLocal()
try:
    repo = EmployeeRepository(db)
    test_id = normalize_emp_id("0001")
    print(f"Searching for Normalized ID: '{test_id}'")
    emp = repo.get_by_emp_id(test_id)
    if emp:
        print(f"Found: {emp.full_name} with emp_id '{emp.emp_id}'")
    else:
        print("NOT FOUND")
        
    print("\nListing first 5 employees again:")
    all_emps = repo.get_all()
    for e in all_emps[:5]:
        print(f" - ID: '{e.emp_id}' | Type: {type(e.emp_id)}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
