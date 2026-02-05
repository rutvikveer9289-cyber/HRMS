from app.core.database import SessionLocal
from app.models.models import Employee
from passlib.context import CryptContext
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(Employee).filter(Employee.email == "admin@rbis.com").first()
        if not admin:
            print("Seeding default admin user...")
            hashed_password = pwd_context.hash("Admin@123")
            new_admin = Employee(
                emp_id="RBIS001",
                first_name="Super",
                last_name="Admin",
                full_name="Super Admin",
                email="admin@rbis.com",
                password_hash=hashed_password,
                role="SUPER_ADMIN",
                designation="Administrator",
                is_verified=True,
                status="Active"
            )
            db.add(new_admin)
            db.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
