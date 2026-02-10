"""
Update PF Deduction Percentage
This script allows you to change PF deduction for specific employees or all employees
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import EmployeeDeduction, DeductionType
from datetime import date

def update_pf_for_employee(emp_id: str, new_percentage: float):
    """Update PF deduction for a specific employee"""
    db = SessionLocal()
    
    try:
        # Get PF deduction type
        pf_type = db.query(DeductionType).filter(DeductionType.name == "PF").first()
        if not pf_type:
            print("❌ PF deduction type not found!")
            return
        
        # Find active PF deduction for employee
        pf_deduction = db.query(EmployeeDeduction).filter(
            EmployeeDeduction.emp_id == emp_id,
            EmployeeDeduction.deduction_type_id == pf_type.id,
            EmployeeDeduction.is_active == True
        ).first()
        
        if not pf_deduction:
            print(f"❌ No active PF deduction found for {emp_id}")
            return
        
        old_value = pf_deduction.value
        pf_deduction.value = new_percentage
        db.commit()
        
        print(f"✓ Updated PF for {emp_id}: {old_value}% → {new_percentage}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def update_pf_for_all(new_percentage: float):
    """Update PF deduction for all employees"""
    db = SessionLocal()
    
    try:
        # Get PF deduction type
        pf_type = db.query(DeductionType).filter(DeductionType.name == "PF").first()
        if not pf_type:
            print("❌ PF deduction type not found!")
            return
        
        # Find all active PF deductions
        pf_deductions = db.query(EmployeeDeduction).filter(
            EmployeeDeduction.deduction_type_id == pf_type.id,
            EmployeeDeduction.is_active == True
        ).all()
        
        if not pf_deductions:
            print("❌ No active PF deductions found!")
            return
        
        print(f"\nUpdating PF to {new_percentage}% for {len(pf_deductions)} employees...\n")
        
        for deduction in pf_deductions:
            old_value = deduction.value
            deduction.value = new_percentage
            print(f"  ✓ {deduction.emp_id}: {old_value}% → {new_percentage}%")
        
        db.commit()
        print(f"\n✓ Successfully updated PF to {new_percentage}% for all employees!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def remove_pf_for_employee(emp_id: str):
    """Remove PF deduction for a specific employee"""
    db = SessionLocal()
    
    try:
        # Get PF deduction type
        pf_type = db.query(DeductionType).filter(DeductionType.name == "PF").first()
        if not pf_type:
            print("❌ PF deduction type not found!")
            return
        
        # Find active PF deduction for employee
        pf_deduction = db.query(EmployeeDeduction).filter(
            EmployeeDeduction.emp_id == emp_id,
            EmployeeDeduction.deduction_type_id == pf_type.id,
            EmployeeDeduction.is_active == True
        ).first()
        
        if not pf_deduction:
            print(f"❌ No active PF deduction found for {emp_id}")
            return
        
        # Deactivate the deduction
        pf_deduction.is_active = False
        pf_deduction.effective_to = date.today()
        db.commit()
        
        print(f"✓ Removed PF deduction for {emp_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("PF Deduction Management Tool")
    print("=" * 60)
    print("\nOptions:")
    print("1. Update PF for a specific employee")
    print("2. Update PF for ALL employees")
    print("3. Remove PF for a specific employee")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        emp_id = input("Enter Employee ID (e.g., RBIS0002): ").strip()
        new_pct = float(input("Enter new PF percentage (e.g., 10): ").strip())
        update_pf_for_employee(emp_id, new_pct)
    
    elif choice == "2":
        new_pct = float(input("Enter new PF percentage for ALL employees (e.g., 10): ").strip())
        confirm = input(f"⚠️  This will change PF to {new_pct}% for ALL employees. Continue? (yes/no): ").strip().lower()
        if confirm == "yes":
            update_pf_for_all(new_pct)
        else:
            print("Cancelled.")
    
    elif choice == "3":
        emp_id = input("Enter Employee ID to remove PF (e.g., RBIS0002): ").strip()
        confirm = input(f"⚠️  This will remove PF deduction for {emp_id}. Continue? (yes/no): ").strip().lower()
        if confirm == "yes":
            remove_pf_for_employee(emp_id)
        else:
            print("Cancelled.")
    
    else:
        print("Invalid choice!")
