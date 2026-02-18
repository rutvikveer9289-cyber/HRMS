from app.core.database import SessionLocal
from app.models.employee import Employee
db = SessionLocal()
count = db.query(Employee).count()
print(f"Total employees: {count}")
db.close()
