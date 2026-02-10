"""
Add IFSC Code Column to Employees Table
This script adds the bank_ifsc_code column to the employees table
"""
from sqlalchemy import create_engine, text
from app.core.config import get_settings

def add_ifsc_code_column():
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        print("=" * 80)
        print("ADDING IFSC CODE COLUMN TO EMPLOYEES TABLE")
        print("=" * 80)
        
        with engine.connect() as conn:
            # Check if column already exists
            print("\n[1/2] Checking if bank_ifsc_code column exists...")
            
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'employees' 
                AND COLUMN_NAME = 'bank_ifsc_code'
            """))
            
            existing = result.fetchone()
            
            if existing:
                print("✓ Column 'bank_ifsc_code' already exists!")
                print("\nNo changes needed.")
                return
            
            print("ℹ️  Column 'bank_ifsc_code' does not exist")
            
            # Add the column
            print("\n[2/2] Adding bank_ifsc_code column...")
            conn.execute(text("""
                ALTER TABLE employees 
                ADD bank_ifsc_code VARCHAR(11) NULL
            """))
            conn.commit()
            
            print("✓ Column 'bank_ifsc_code' added successfully!")
            
            print("\n" + "=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print("✅ IFSC code column added to employees table")
            print("\nEmployees can now enter:")
            print("  • Bank Name")
            print("  • Account Number")
            print("  • IFSC Code (NEW!)")
            print("=" * 80)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

if __name__ == "__main__":
    add_ifsc_code_column()
