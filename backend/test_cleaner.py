import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.cleaner import detect_and_clean_memory
import pandas as pd

file_path = r"d:\HRMS\rbis-hrms-main\files\EmployeeInOutDurationDailyAttendance RBIS.xls"

with open(file_path, "rb") as f:
    content = f.read()

from app.utils.file_utils import normalize_emp_id

cleaned_data, detected_type = detect_and_clean_memory(content)
print(f"Detected Type: {detected_type}")
if cleaned_data:
    print(f"Total records cleaned: {len(cleaned_data)}")
    print("First 3 records sample:")
    for rec in cleaned_data[:3]:
        raw_id = str(rec.get('EmpID', '')).strip()
        normalized_id = normalize_emp_id(raw_id)
        print(f" - Date: {rec.get('Date')} | RawEmpID: '{raw_id}' | Normalized: '{normalized_id}' | Status: {rec.get('Attendance')}")
else:
    print("CLEANING FAILED")
