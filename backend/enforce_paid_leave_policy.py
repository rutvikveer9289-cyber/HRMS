"""
Enforce Paid Leave Only Policy
Updates all existing leave types to be paid and sets database constraint
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.leave import LeaveType
from sqlalchemy import text

def enforce_paid_leave_policy():
    """Ensure all leave types are paid"""
    db = SessionLocal()
    try:
        print("Enforcing PAID LEAVE ONLY policy...")
        
        # Get all leave types
        leave_types = db.query(LeaveType).all()
        
        print(f"\nFound {len(leave_types)} leave type(s)")
        
        updated_count = 0
        for leave_type in leave_types:
            if not leave_type.is_paid:
                print(f"  ⚠️  Converting '{leave_type.name}' to PAID leave")
                leave_type.is_paid = True
                updated_count += 1
            else:
                print(f"  ✅ '{leave_type.name}' is already PAID")
        
        if updated_count > 0:
            db.commit()
            print(f"\n✅ Updated {updated_count} leave type(s) to PAID")
        else:
            print("\n✅ All leave types are already PAID")
        
        # Update database constraint to enforce paid leave
        print("\nUpdating database constraint...")
        try:
            # For SQL Server, add a check constraint
            db.execute(text("""
                IF NOT EXISTS (
                    SELECT * FROM sys.check_constraints 
                    WHERE name = 'CK_LeaveTypes_IsPaid'
                )
                BEGIN
                    ALTER TABLE leave_types 
                    ADD CONSTRAINT CK_LeaveTypes_IsPaid 
                    CHECK (is_paid = 1)
                END
            """))
            db.commit()
            print("✅ Database constraint added: All leave types MUST be paid")
        except Exception as e:
            print(f"⚠️  Could not add constraint (may already exist): {e}")
        
        # Display final summary
        print("\n" + "="*60)
        print("PAID LEAVE POLICY SUMMARY")
        print("="*60)
        
        leave_types = db.query(LeaveType).all()
        for lt in leave_types:
            status = "✅ PAID" if lt.is_paid else "❌ UNPAID"
            print(f"  {status} | {lt.name} | Quota: {lt.annual_quota} days/year")
        
        print("="*60)
        print("\n✅ Policy enforcement complete!")
        print("📋 All leaves in the system are now PAID LEAVE")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    enforce_paid_leave_policy()
