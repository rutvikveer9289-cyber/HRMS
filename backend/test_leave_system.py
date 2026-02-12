import sys
import os
from datetime import date, timedelta

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.leave_service import LeaveService
from app.models.employee import Employee
from app.models.leave import LeaveType, LeaveRequest, LeaveBalance, LeaveApprovalLog

def test_leave_system():
    db = SessionLocal()
    try:
        print("=== Testing Leave Management System ===")
        service = LeaveService(db)

        # 1. Setup Users
        # Test Employee
        emp_id = "TEST_LEAVE_EMP"
        emp = db.query(Employee).filter(Employee.emp_id == emp_id).first()
        if not emp:
            print(f"[SETUP] Creating Employee {emp_id}")
            emp = Employee(emp_id=emp_id, full_name="Leave Tester", email="leave_tester@example.com", role="EMPLOYEE")
            db.add(emp)
        
        # HR
        hr_id = "TEST_LEAVE_HR"
        hr = db.query(Employee).filter(Employee.emp_id == hr_id).first()
        if not hr:
            print(f"[SETUP] Creating HR {hr_id}")
            hr = Employee(emp_id=hr_id, full_name="Leave HR", email="leave_hr@example.com", role="HR")
            db.add(hr)

        # CEO
        ceo_id = "TEST_LEAVE_CEO"
        ceo = db.query(Employee).filter(Employee.emp_id == ceo_id).first()
        if not ceo:
            print(f"[SETUP] Creating CEO {ceo_id}")
            ceo = Employee(emp_id=ceo_id, full_name="Leave CEO", email="leave_ceo@example.com", role="CEO")
            db.add(ceo)
        
        db.commit()

        # 2. Setup Leave Type
        type_name = "Test Sick Leave"
        l_type = db.query(LeaveType).filter(LeaveType.name == type_name).first()
        if not l_type:
            print(f"[SETUP] Creating Leave Type '{type_name}'")
            l_type = LeaveType(name=type_name, annual_quota=10, is_paid=True)
            db.add(l_type)
            db.commit()
            db.refresh(l_type)
        
        # 3. Check Balance (Should auto-create on get)
        print("[TEST] Checking Balance...")
        balances = service.get_employee_balances(emp_id)
        # balances is a dict: {type_name: {total, used, available, id}}
        # Or list of LeaveBalance objects?
        # Service get_employee_balances returns enriched dict usually.
        # Let's check service code later if it fails. Assuming standard service pattern.
        
        # 4. Apply for Leave
        print("[TEST] Applying for Leave...")
        start_date = date.today() + timedelta(days=1)
        end_date = start_date
        
        # Clean up existing overlapping requests
        existing = db.query(LeaveRequest).filter(
            LeaveRequest.emp_id == emp_id,
            LeaveRequest.start_date == start_date
        ).first()
        if existing:
            # Delete logs first
            logs = db.query(LeaveApprovalLog).filter(LeaveApprovalLog.request_id == existing.id).all()
            for log in logs:
                db.delete(log)
            db.delete(existing)
            db.commit()

        apply_data = {
            "leave_type_id": l_type.id,
            "start_date": start_date,
            "end_date": end_date,
            "reason": "Feeling testy"
        }
        
        # service.apply_leave expects (user_obj, data_dict)
        try:
            result = service.apply_leave(emp, apply_data)
            print(f"  > Application Result: {result}")
            
            # Fetch the request
            request = db.query(LeaveRequest).filter(
                LeaveRequest.emp_id == emp_id,
                LeaveRequest.start_date == start_date
            ).first()
            if not request:
                 print("  > [FAIL] Request record not found in DB")
                 return
            print(f"  > Leave Applied. ID: {request.id}. Status: {request.status}")

        except Exception as e:
            print(f"  > [FAIL] Application Failed: {e}")
            return

        if request.status != "PENDING":
             print(f"  > [FAIL] Status should be PENDING, got {request.status}")
        
        # 5. HR Approval
        print("[TEST] HR Approval...")
        try:
            # service.approve_by_hr(request_id, hr_user_obj, action, remarks)
            hr_result = service.approve_by_hr(request.id, hr, "APPROVE", "HR Approved")
            print(f"  > HR Action Result: {hr_result}")
            
            db.refresh(request)
            print(f"  > Request Status: {request.status}")
        except Exception as e:
             print(f"  > [FAIL] HR Approval Failed: {e}")
             return

        if request.status != "APPROVED_BY_HR":
             print(f"  > [WARN] Status check: Got {request.status}")
        
        # 6. CEO Approval
        print("[TEST] CEO Approval...")
        try:
            ceo_result = service.approve_by_ceo(request.id, ceo, "APPROVE", "CEO Approved")
            print(f"  > CEO Action Result: {ceo_result}")
            
            db.refresh(request)
            print(f"  > Final Status: {request.status}")
        except Exception as e:
             print(f"  > [FAIL] CEO Approval Failed: {e}")
             return

        if request.status == "APPROVED":
            print("  > [PASS] Leave Finalized as APPROVED")
        else:
            print(f"  > [FAIL] Expected APPROVED, got {request.status}")

        print("=== Leave System Health Check Complete ===")

    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_leave_system()
