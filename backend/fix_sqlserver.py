
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
    else:
        print("payroll_records table not found. Triggering create_all...")
        from app.models.models import Base
        Base.metadata.create_all(bind=engine)
        print("Tables created.")
