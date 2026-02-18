import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.attendance import Attendance
from app.models.file_upload import FileUploadLog

db = SessionLocal()
try:
    att_count = db.query(Attendance).count()
    file_count = db.query(FileUploadLog).count()
    print(f"Total Attendance Records: {att_count}")
    print(f"Total Upload Logs: {file_count}")
    
    recent_files = db.query(FileUploadLog).order_by(FileUploadLog.uploaded_at.desc()).limit(3).all()
    print("\nRecent Uploads:")
    for f in recent_files:
        print(f" - {f.filename} at {f.uploaded_at}")
        
    recent_att = db.query(Attendance).order_by(Attendance.date.desc()).limit(10).all()
    print("\nRecent Attendance:")
    for a in recent_att:
        print(f" - {a.emp_id} | {a.date} | {a.attendance_status}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
