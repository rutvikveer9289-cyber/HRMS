"""
Complete PF Removal Tool
This script removes PF deduction from all employees and deactivates the PF type
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import DeductionType, EmployeeDeduction
from datetime import date

def remove_pf_completely():
    """Remove PF from all employees and deactivate the PF type"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("COMPLETE PF REMOVAL TOOL")
        print("=" * 80)
        
        # Step 1: Find PF deduction type
        print("\n[1/3] Locating PF deduction type...")
        pf_type = db.query(DeductionType).filter(DeductionType.name == "PF").first()
        
        if not pf_type:
            print("❌ PF deduction type not found!")
            print("Nothing to remove.")
            return
        
        print(f"✓ Found PF type (ID: {pf_type.id})")
        print(f"  Current status: {'Active' if pf_type.is_active else 'Inactive'}")
        print(f"  Default value: {pf_type.default_value}%")
        
        # Step 2: Find all employees with PF deduction
        print("\n[2/3] Finding employees with PF deduction...")
        pf_deductions = db.query(EmployeeDeduction).filter(
            EmployeeDeduction.deduction_type_id == pf_type.id,
            EmployeeDeduction.is_active == True
        ).all()
        
        if not pf_deductions:
            print("ℹ️  No active PF deductions found for any employee.")
        else:
            print(f"✓ Found {len(pf_deductions)} employees with active PF deduction")
            print("\nEmployees with PF:")
            for deduction in pf_deductions:
                print(f"  • {deduction.emp_id} - {deduction.value}% PF")
        
        # Confirmation
        print("\n" + "=" * 80)
        print("⚠️  WARNING: This will:")
        print("=" * 80)
        if pf_deductions:
            print(f"1. Remove PF deduction from {len(pf_deductions)} employees")
        print("2. Deactivate the PF deduction type")
        print("3. Employees will no longer have PF deducted from salary")
        print("\nThis action can be reversed by running setup_default_pf.py again.")
        print("=" * 80)
        
        confirm = input("\nDo you want to proceed? (type 'YES' to confirm): ").strip()
        
        if confirm != "YES":
            print("\n❌ Operation cancelled.")
            return
        
        # Step 3: Remove PF from all employees
        if pf_deductions:
            print("\n[3/3] Removing PF from employees...")
            removed_count = 0
            
            for deduction in pf_deductions:
                deduction.is_active = False
                deduction.effective_to = date.today()
                print(f"  ✓ Removed PF from {deduction.emp_id}")
                removed_count += 1
            
            db.commit()
            print(f"\n✓ Removed PF from {removed_count} employees")
        else:
            print("\n[3/3] No employee deductions to remove")
        
        # Step 4: Deactivate PF type
        print("\n[4/4] Deactivating PF deduction type...")
        pf_type.is_active = False
        db.commit()
        print("✓ PF deduction type deactivated")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        if pf_deductions:
            print(f"✓ Removed PF from {len(pf_deductions)} employees")
        print("✓ Deactivated PF deduction type")
        print("\n✅ PF deduction has been completely removed from the system!")
        print("\nNext steps:")
        print("• Process payroll - employees will no longer have PF deducted")
        print("• To restore PF, run: python setup_default_pf.py")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def restore_pf():
    """Quick restore option"""
    print("\n" + "=" * 80)
    print("To restore PF deduction, run:")
    print("  python setup_default_pf.py")
    print("=" * 80)

if __name__ == "__main__":
    remove_pf_completely()
