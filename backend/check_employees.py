import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.employee import Employee

db = SessionLocal()
try:
    emps = db.query(Employee).limit(20).all()
    print(f"Total Employees: {db.query(Employee).count()}")
    for e in emps:
        print(f" - ID: '{e.emp_id}' | Name: {e.full_name}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
