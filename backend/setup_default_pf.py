"""
Setup Default PF Deduction (12%)
This script creates a PF deduction type and assigns it to all active employees
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.models import Employee, DeductionType, EmployeeDeduction
from datetime import date

def setup_default_pf():
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Setting up default 12% PF deduction for all employees")
        print("=" * 60)
        
        # Step 1: Check if PF deduction type already exists
        pf_type = db.query(DeductionType).filter(DeductionType.name == "PF").first()
        
        if not pf_type:
            print("\n[1/3] Creating PF deduction type...")
            pf_type = DeductionType(
                name="PF",
                description="Provident Fund - 12% of Basic Salary",
                calculation_type="PERCENTAGE",
                default_value=12.0,
                is_mandatory=True,
                is_active=True
            )
            db.add(pf_type)
            db.commit()
            db.refresh(pf_type)
            print(f"✓ PF deduction type created (ID: {pf_type.id})")
        else:
            print(f"\n[1/3] PF deduction type already exists (ID: {pf_type.id})")
            # Update to ensure it's 12%
            pf_type.default_value = 12.0
            pf_type.calculation_type = "PERCENTAGE"
            pf_type.is_mandatory = True
            pf_type.is_active = True
            db.commit()
            print("✓ Updated PF deduction type to 12%")
        
        # Step 2: Get all active employees
        print("\n[2/3] Fetching all active employees...")
        active_employees = db.query(Employee).filter(
            Employee.status == "ACTIVE",
            Employee.emp_id.isnot(None)
        ).all()
        
        print(f"✓ Found {len(active_employees)} active employees")
        
        # Step 3: Assign PF to employees who don't have it
        print("\n[3/3] Assigning PF deduction to employees...")
        assigned_count = 0
        skipped_count = 0
        
        for employee in active_employees:
            # Check if employee already has PF deduction
            existing_pf = db.query(EmployeeDeduction).filter(
                EmployeeDeduction.emp_id == employee.emp_id,
                EmployeeDeduction.deduction_type_id == pf_type.id,
                EmployeeDeduction.is_active == True
            ).first()
            
            if existing_pf:
                print(f"  ⊙ {employee.emp_id} ({employee.full_name}) - Already has PF")
                skipped_count += 1
            else:
                # Assign PF deduction
                emp_deduction = EmployeeDeduction(
                    emp_id=employee.emp_id,
                    deduction_type_id=pf_type.id,
                    calculation_type="PERCENTAGE",
                    value=12.0,
                    is_active=True,
                    effective_from=date.today(),
                    effective_to=None
                )
                db.add(emp_deduction)
                print(f"  ✓ {employee.emp_id} ({employee.full_name}) - PF assigned (12%)")
                assigned_count += 1
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total employees processed: {len(active_employees)}")
        print(f"New PF assignments: {assigned_count}")
        print(f"Already had PF: {skipped_count}")
        print("\n✓ Default 12% PF deduction setup complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_default_pf()
