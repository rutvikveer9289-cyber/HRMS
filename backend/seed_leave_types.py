from app.core.database import SessionLocal
from app.models.leave import LeaveType

def seed_leave_types():
    db = SessionLocal()
    try:
        leave_types = [
            {"name": "Paid Leave", "annual_quota": 20, "is_paid": True},
            {"name": "Sick Leave", "annual_quota": 10, "is_paid": True},
            {"name": "Casual Leave", "annual_quota": 8, "is_paid": True},
            {"name": "Unpaid Leave", "annual_quota": 0, "is_paid": False},
        ]
        
        for lt_data in leave_types:
            existing = db.query(LeaveType).filter(LeaveType.name == lt_data["name"]).first()
            if not existing:
                print(f"Seeding leave type: {lt_data['name']}")
                db.add(LeaveType(**lt_data))
        
        db.commit()
        print("Leave types seeded successfully!")
    except Exception as e:
        print(f"Error seeding leave types: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_leave_types()
