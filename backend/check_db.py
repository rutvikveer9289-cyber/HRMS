from app.core.database import SessionLocal
from app.models.employee import Employee
db = SessionLocal()
emps = db.query(Employee).filter(Employee.emp_id == 'RBIS0001').all()
for e in emps:
    print(f"ID: {e.emp_id}, Email: {e.email}, Name: {e.full_name}")
db.close()
