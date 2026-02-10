"""
Delete Deduction Type
This script allows you to delete or deactivate deduction types
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import DeductionType, EmployeeDeduction

def list_all_deduction_types():
    """List all deduction types"""
    db = SessionLocal()
    
    try:
        types = db.query(DeductionType).all()
        
        if not types:
            print("No deduction types found!")
            return []
        
        print("\n" + "=" * 80)
        print("EXISTING DEDUCTION TYPES")
        print("=" * 80)
        print(f"{'ID':<5} {'Name':<20} {'Type':<15} {'Value':<10} {'Active':<10}")
        print("-" * 80)
        
        for dt in types:
            active_status = "✓ Yes" if dt.is_active else "✗ No"
            print(f"{dt.id:<5} {dt.name:<20} {dt.calculation_type:<15} {dt.default_value:<10} {active_status:<10}")
        
        print("=" * 80)
        return types
        
    finally:
        db.close()

def deactivate_deduction_type(type_id: int):
    """Deactivate a deduction type (soft delete)"""
    db = SessionLocal()
    
    try:
        deduction_type = db.query(DeductionType).filter(DeductionType.id == type_id).first()
        
        if not deduction_type:
            print(f"❌ Deduction type with ID {type_id} not found!")
            return
        
        # Check if any employees have this deduction
        active_assignments = db.query(EmployeeDeduction).filter(
            EmployeeDeduction.deduction_type_id == type_id,
            EmployeeDeduction.is_active == True
        ).count()
        
        if active_assignments > 0:
            print(f"\n⚠️  WARNING: {active_assignments} employees currently have this deduction assigned!")
            print("Deactivating this type will NOT remove it from employees.")
            print("You should remove it from employees first using manage_pf.py")
            
            confirm = input("\nContinue anyway? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Cancelled.")
                return
        
        old_status = "Active" if deduction_type.is_active else "Inactive"
        deduction_type.is_active = False
        db.commit()
        
        print(f"\n✓ Deduction type '{deduction_type.name}' deactivated successfully!")
        print(f"  Status: {old_status} → Inactive")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def permanently_delete_deduction_type(type_id: int):
    """Permanently delete a deduction type (hard delete)"""
    db = SessionLocal()
    
    try:
        deduction_type = db.query(DeductionType).filter(DeductionType.id == type_id).first()
        
        if not deduction_type:
            print(f"❌ Deduction type with ID {type_id} not found!")
            return
        
        # Check if any employees have this deduction (active or inactive)
        total_assignments = db.query(EmployeeDeduction).filter(
            EmployeeDeduction.deduction_type_id == type_id
        ).count()
        
        if total_assignments > 0:
            print(f"\n❌ CANNOT DELETE: {total_assignments} employees have this deduction in their history!")
            print("You must first remove ALL employee deductions using this type.")
            print("\nOptions:")
            print("1. Use 'Deactivate' instead (soft delete)")
            print("2. Manually remove all employee deductions first")
            return
        
        type_name = deduction_type.name
        db.delete(deduction_type)
        db.commit()
        
        print(f"\n✓ Deduction type '{type_name}' permanently deleted!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def reactivate_deduction_type(type_id: int):
    """Reactivate a deduction type"""
    db = SessionLocal()
    
    try:
        deduction_type = db.query(DeductionType).filter(DeductionType.id == type_id).first()
        
        if not deduction_type:
            print(f"❌ Deduction type with ID {type_id} not found!")
            return
        
        if deduction_type.is_active:
            print(f"ℹ️  Deduction type '{deduction_type.name}' is already active!")
            return
        
        deduction_type.is_active = True
        db.commit()
        
        print(f"\n✓ Deduction type '{deduction_type.name}' reactivated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("DEDUCTION TYPE MANAGEMENT TOOL")
    print("=" * 80)
    
    # List all types first
    types = list_all_deduction_types()
    
    if not types:
        exit()
    
    print("\nOptions:")
    print("1. Deactivate a deduction type (soft delete - recommended)")
    print("2. Permanently delete a deduction type (hard delete - dangerous!)")
    print("3. Reactivate a deduction type")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1/2/3/4): ").strip()
    
    if choice == "1":
        type_id = int(input("\nEnter Deduction Type ID to deactivate: ").strip())
        deactivate_deduction_type(type_id)
    
    elif choice == "2":
        print("\n⚠️  WARNING: This will PERMANENTLY delete the deduction type!")
        print("This action CANNOT be undone!")
        type_id = int(input("\nEnter Deduction Type ID to delete: ").strip())
        confirm = input(f"Are you ABSOLUTELY SURE you want to delete type ID {type_id}? (type 'DELETE' to confirm): ").strip()
        if confirm == "DELETE":
            permanently_delete_deduction_type(type_id)
        else:
            print("Cancelled.")
    
    elif choice == "3":
        type_id = int(input("\nEnter Deduction Type ID to reactivate: ").strip())
        reactivate_deduction_type(type_id)
    
    elif choice == "4":
        print("Exiting...")
    
    else:
        print("Invalid choice!")
