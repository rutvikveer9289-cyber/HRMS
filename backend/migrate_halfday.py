import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.attendance import Attendance

db = SessionLocal()
try:
    # Update all Half Day records to Present
    affected_rows = db.query(Attendance).filter(Attendance.attendance_status == "Half Day").update({"attendance_status": "Present"})
    db.commit()
    print(f"Successfully converted {affected_rows} 'Half Day' records to 'Present'.")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
