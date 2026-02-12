"""
Database Migration Script
Adds new attendance tracking columns to payroll_records table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from sqlalchemy import text

def migrate():
    """Add on_leave_days and half_days columns to payroll_records"""
    db = SessionLocal()
    try:
        print("Starting database migration...")
        print(f"Database: {engine.url}")
        
        # Check if columns already exist (SQL Server syntax)
        check_columns_sql = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'payroll_records'
        """
        
        result = db.execute(text(check_columns_sql))
        columns = [row[0] for row in result.fetchall()]
        
        print(f"Found {len(columns)} existing columns in payroll_records table")
        
        migrations_needed = []
        
        if 'on_leave_days' not in columns:
            migrations_needed.append("ALTER TABLE payroll_records ADD on_leave_days INT NULL")
            
        if 'half_days' not in columns:
            migrations_needed.append("ALTER TABLE payroll_records ADD half_days INT NULL")
        
        if migrations_needed:
            print(f"Found {len(migrations_needed)} migrations to apply...")
            
            for migration_sql in migrations_needed:
                print(f"Executing: {migration_sql}")
                db.execute(text(migration_sql))
            
            db.commit()
            print("✅ Migration completed successfully!")
            print("New columns added:")
            print("  - on_leave_days (INT NULL)")
            print("  - half_days (INT NULL)")
        else:
            print("✅ Database is already up to date. No migrations needed.")
        
        # Show current schema
        print("\nCurrent payroll_records columns:")
        result = db.execute(text(check_columns_sql))
        for row in result.fetchall():
            print(f"  - {row[0]}")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
