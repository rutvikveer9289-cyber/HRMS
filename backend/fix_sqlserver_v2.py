
from sqlalchemy import create_engine, text
import os
from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    print("Checking tables in SQL Server...")
    result = conn.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"))
    tables = [row[0] for row in result]
    print(f"Tables: {tables}")
    
    if 'employees' in tables:
        print("Checking columns in employees...")
        result = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'employees'"))
        columns = [row[0] for row in result]
        print(f"Columns in employees: {columns}")
        
        new_columns = {
            'department': 'NVARCHAR(100)',
            'location': 'NVARCHAR(100)',
            'bank_name': 'NVARCHAR(100)',
            'bank_account_no': 'NVARCHAR(50)'
        }
        
        for col, col_type in new_columns.items():
            if col not in columns:
                print(f"Adding {col} column...")
                conn.execute(text(f"ALTER TABLE employees ADD {col} {col_type}"))
                conn.commit()
                print(f"Column {col} added.")
            else:
                print(f"Column {col} already exists.")
    else:
        print("Employees table not found!")

    if 'payroll_records' in tables:
        print("Checking columns in payroll_records...")
        result = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'payroll_records'"))
        columns = [row[0] for row in result]
        if 'payment_method' not in columns:
            print("Adding payment_method column...")
            conn.execute(text("ALTER TABLE payroll_records ADD payment_method NVARCHAR(50)"))
            conn.commit()
            print("Column added.")
        else:
            print("payment_method already exists.")
