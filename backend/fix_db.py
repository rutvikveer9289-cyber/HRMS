
import sqlite3
import os

db_path = "hrms.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if payment_method exists
    cursor.execute("PRAGMA table_info(payroll_records)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "payment_method" not in columns:
        print("Adding payment_method column to payroll_records...")
        cursor.execute("ALTER TABLE payroll_records ADD COLUMN payment_method VARCHAR(50)")
        conn.commit()
        print("Column added successfully.")
    else:
        print("payment_method column already exists.")
    
    conn.close()
else:
    print("Database file not found.")
