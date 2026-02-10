"""
Flexible Deduction Type Deletion Tool
Delete all deduction types or select specific ones
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import DeductionType, EmployeeDeduction
from datetime import date

def list_all_types():
    """List all deduction types and return them"""
    db = SessionLocal()
    try:
        types = db.query(DeductionType).all()
        
        if not types:
            print("\n✓ No deduction types found - database is clean!")
            return []
        
        print("\n" + "=" * 80)
        print("EXISTING DEDUCTION TYPES")
        print("=" * 80)
        print(f"{'ID':<5} {'Name':<20} {'Type':<15} {'Value':<10} {'Active':<10} {'Employees':<12}")
        print("-" * 80)
        
        for dt in types:
            active_status = "✓ Yes" if dt.is_active else "✗ No"
            # Count employees with this deduction
            emp_count = db.query(EmployeeDeduction).filter(
                EmployeeDeduction.deduction_type_id == dt.id,
                EmployeeDeduction.is_active == True
            ).count()
            emp_text = f"{emp_count} active"
            
            print(f"{dt.id:<5} {dt.name:<20} {dt.calculation_type:<15} {dt.default_value or 0:<10} {active_status:<10} {emp_text:<12}")
        
        print("=" * 80)
        return types
    finally:
        db.close()

def delete_all_types():
    """Delete all deduction types"""
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 80)
        print("DELETE ALL DEDUCTION TYPES")
        print("=" * 80)
        
        # Get all types
        all_types = db.query(DeductionType).all()
        
        if not all_types:
            print("✓ No deduction types to delete!")
            return
        
        # Check for employee assignments
        total_assignments = 0
        for dt in all_types:
            count = db.query(EmployeeDeduction).filter(
                EmployeeDeduction.deduction_type_id == dt.id,
                EmployeeDeduction.is_active == True
            ).count()
            total_assignments += count
        
        print(f"\nFound {len(all_types)} deduction types")
        if total_assignments > 0:
            print(f"⚠️  WARNING: {total_assignments} active employee deductions will be removed!")
        
        print("\nThis will:")
        print("1. Remove all deductions from employees")
        print("2. Delete all deduction types")
        print("3. Clean slate - you can start fresh")
        
        confirm = input("\nType 'DELETE ALL' to confirm: ").strip()
        
        if confirm != "DELETE ALL":
            print("\n❌ Operation cancelled.")
            return
        
        # Step 1: Remove all employee deductions
        if total_assignments > 0:
            print("\n[1/2] Removing deductions from employees...")
            removed = 0
            for dt in all_types:
                deductions = db.query(EmployeeDeduction).filter(
                    EmployeeDeduction.deduction_type_id == dt.id,
                    EmployeeDeduction.is_active == True
                ).all()
                
                for ded in deductions:
                    ded.is_active = False
                    ded.effective_to = date.today()
                    removed += 1
            
            db.commit()
            print(f"✓ Removed {removed} employee deductions")
        else:
            print("\n[1/2] No employee deductions to remove")
        
        # Step 2: Delete all types
        print("\n[2/2] Deleting deduction types...")
        deleted_names = [dt.name for dt in all_types]
        
        for dt in all_types:
            db.delete(dt)
        
        db.commit()
        
        print(f"✓ Deleted {len(all_types)} deduction types:")
        for name in deleted_names:
            print(f"  • {name}")
        
        print("\n" + "=" * 80)
        print("✅ ALL DEDUCTION TYPES DELETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def delete_selected_types(type_ids):
    """Delete specific deduction types by ID"""
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 80)
        print("DELETE SELECTED DEDUCTION TYPES")
        print("=" * 80)
        
        deleted_count = 0
        
        for type_id in type_ids:
            dt = db.query(DeductionType).filter(DeductionType.id == type_id).first()
            
            if not dt:
                print(f"\n⚠️  Type ID {type_id} not found - skipping")
                continue
            
            # Check for employee assignments
            emp_count = db.query(EmployeeDeduction).filter(
                EmployeeDeduction.deduction_type_id == type_id,
                EmployeeDeduction.is_active == True
            ).count()
            
            print(f"\nDeleting: {dt.name} (ID: {type_id})")
            if emp_count > 0:
                print(f"  ⚠️  {emp_count} employees have this deduction")
                
                # Remove from employees first
                deductions = db.query(EmployeeDeduction).filter(
                    EmployeeDeduction.deduction_type_id == type_id,
                    EmployeeDeduction.is_active == True
                ).all()
                
                for ded in deductions:
                    ded.is_active = False
                    ded.effective_to = date.today()
                
                print(f"  ✓ Removed from {emp_count} employees")
            
            # Delete the type
            db.delete(dt)
            print(f"  ✓ Deleted type '{dt.name}'")
            deleted_count += 1
        
        db.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Successfully deleted {deleted_count} deduction type(s)!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("DEDUCTION TYPE DELETION TOOL")
    print("=" * 80)
    
    # List all types
    types = list_all_types()
    
    if not types:
        exit()
    
    print("\nOptions:")
    print("1. Delete ALL deduction types (clean slate)")
    print("2. Delete specific deduction type(s)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        delete_all_types()
    
    elif choice == "2":
        print("\nEnter deduction type IDs to delete (comma-separated)")
        print("Example: 1,2,3  or just  2")
        ids_input = input("\nIDs to delete: ").strip()
        
        try:
            type_ids = [int(id.strip()) for id in ids_input.split(",")]
            
            print(f"\nYou selected: {type_ids}")
            confirm = input("Proceed with deletion? (yes/no): ").strip().lower()
            
            if confirm == "yes":
                delete_selected_types(type_ids)
            else:
                print("\n❌ Operation cancelled.")
        except ValueError:
            print("\n❌ Invalid input! Please enter numbers separated by commas.")
    
    elif choice == "3":
        print("\nExiting...")
    
    else:
        print("\n❌ Invalid choice!")
