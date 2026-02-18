"""
Leave Service
Business logic for leave management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date, datetime, timedelta
from typing import List, Dict

from app.repositories.leave_repository import LeaveRepository
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.employee_repository import EmployeeRepository
from app.services.communication_service import CommunicationService
from app.models.models import Employee, UserRole

class LeaveService:
    """Handles leave management business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.leave_repo = LeaveRepository(db)
        self.attendance_repo = AttendanceRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.comm_service = CommunicationService(db)
    
    def create_leave_type(self, type_data: dict) -> Dict:
        """
        Create new leave type
        
        Args:
            type_data: Leave type information
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If leave type already exists
        """
        existing = self.leave_repo.get_leave_type_by_name(type_data['name'])
        if existing:
            raise HTTPException(status_code=400, detail="Leave type already exists")
        
        self.leave_repo.create_leave_type(type_data)
        self.leave_repo.commit()
        
        return {"message": f"Leave type {type_data['name']} created"}
    
    def get_active_leave_types(self) -> List:
        """Get all active leave types"""
        return self.leave_repo.get_active_leave_types()
    
    def get_employee_balances(self, emp_id: str, year: int = None) -> List:
        """
        Get leave balances for employee
        
        Args:
            emp_id: Employee ID
            year: Year (defaults to current year)
            
        Returns:
            List of leave balances
        """
        if year is None:
            year = datetime.now().year
        
        balances = self.leave_repo.get_balances_by_emp(emp_id, year)
        
        # Initialize balances if they don't exist
        if not balances:
            balances = self._initialize_balances(emp_id, year)
        
        return balances
    
    def _initialize_balances(self, emp_id: str, year: int) -> List:
        """Initialize leave balances for employee"""
        types = self.leave_repo.get_active_leave_types()
        
        for leave_type in types:
            balance_data = {
                "emp_id": emp_id,
                "leave_type_id": leave_type.id,
                "year": year,
                "allocated": leave_type.annual_quota,
                "used": 0
            }
            self.leave_repo.create_balance(balance_data)
        
        self.leave_repo.commit()
        return self.leave_repo.get_balances_by_emp(emp_id, year)
    
    def apply_leave(self, user: Employee, leave_data: dict) -> Dict:
        """
        Apply for leave
        
        Args:
            user: Employee applying for leave
            leave_data: Leave application data
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If validation fails
        """
        start_date = leave_data['start_date']
        end_date = leave_data['end_date']
        leave_type_id = leave_data['leave_type_id']
        reason = leave_data['reason']
        
        # Validation
        self._validate_leave_dates(start_date, end_date)
        
        # Calculate work days
        work_days = self._calculate_work_days(start_date, end_date)
        if work_days <= 0:
            raise HTTPException(
                status_code=400,
                detail="Requested range contains no work days"
            )
        
        # Check for overlaps
        overlap = self.leave_repo.get_overlapping_requests(user.emp_id, start_date, end_date)
        if overlap:
            raise HTTPException(
                status_code=400,
                detail="You already have a leave request overlapping these dates"
            )
        
        # Check leave type and active status
        leave_type = self.leave_repo.get_leave_type_by_id(leave_type_id)
        if not leave_type or not leave_type.is_active:
            raise HTTPException(status_code=400, detail="Selected leave type is not active or available")

        # Check balance
        year = start_date.year
        balance = self.leave_repo.get_balance(user.emp_id, leave_type_id, year)
        
        if not balance:
            # Initialize balance
            balance_data = {
                "emp_id": user.emp_id,
                "leave_type_id": leave_type.id,
                "year": year,
                "allocated": leave_type.annual_quota,
                "used": 0
            }
            balance = self.leave_repo.create_balance(balance_data)
            self.leave_repo.flush()
        
        # Check sufficient balance
        available = balance.allocated - balance.used
        if available < work_days:
            leave_type = self.leave_repo.get_leave_type_by_id(leave_type_id)
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Requested: {work_days}, Available: {available} ({leave_type.name if leave_type else 'Unknown'})"
            )
        
        # Create request
        is_auto_approve_role = user.role in [UserRole.SUPER_ADMIN, UserRole.CEO]
        request_data = {
            "emp_id": user.emp_id,
            "leave_type_id": leave_type_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": work_days,
            "reason": reason,
            "status": "APPROVED" if is_auto_approve_role else "PENDING"
        }
        
        new_request = self.leave_repo.create_request(request_data)
        
        # Auto-approve for authorized roles
        if is_auto_approve_role:
            self.leave_repo.update_balance_used(balance, work_days)
            self.leave_repo.flush()
            self._sync_attendance_on_approval(new_request)
            self.leave_repo.commit()
            role_name = "Super Admin" if user.role == UserRole.SUPER_ADMIN else "CEO"
            return {"message": f"Leave applied and auto-approved for {role_name}"}
        
        if not is_auto_approve_role:
            # Notify HR about new leave application
            self.comm_service.notify_role(
                UserRole.HR, 
                f"New leave application from {user.full_name} ({user.emp_id})",
                "LEAVE",
                "/leave-management"
            )

        self.leave_repo.commit()
        return {"message": "Leave application submitted successfully"}
    
    def get_my_requests(self, emp_id: str) -> List:
        """Get all leave requests for employee"""
        return self.leave_repo.get_requests_by_emp(emp_id)

    def delete_request(self, request_id: int, user: Employee) -> Dict:
        """
        Delete a leave request
        
        Args:
            request_id: Request ID
            user: Current user
            
        Returns:
            Success message
        """
        request = self.leave_repo.get_request_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Leave request not found")
        
        # Check permissions
        is_admin = user.role in [UserRole.SUPER_ADMIN, UserRole.CEO]
        if not is_admin and request.emp_id != user.emp_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this request")
        
        # Check status (can only delete PENDING unless admin)
        if not is_admin and request.status != "PENDING":
            raise HTTPException(status_code=400, detail="Cannot delete a request that is already processed (Approved/Rejected)")
        
        # Delete associated logs first (if any)
        from app.models.leave import LeaveApprovalLog
        self.db.query(LeaveApprovalLog).filter(LeaveApprovalLog.request_id == request_id).delete()
        
        self.leave_repo.delete_request(request)
        self.leave_repo.commit()
        
        return {"message": "Leave request deleted successfully"}
    
    def get_pending_requests_for_hr(self) -> List:
        """Get pending requests for HR approval"""
        return self.leave_repo.get_pending_requests()
    
    def get_pending_requests_for_ceo(self) -> List:
        """Get requests pending CEO approval"""
        return self.leave_repo.get_hr_approved_requests()
    
    def approve_by_hr(self, request_id: int, hr: Employee, action: str, remarks: str = None) -> Dict:
        """
        HR approval/rejection
        
        Args:
            request_id: Leave request ID
            hr: HR employee
            action: APPROVE or REJECT
            remarks: Optional remarks
            
        Returns:
            Success message
        """
        request = self.leave_repo.get_request_by_id(request_id)
        if not request or request.status != "PENDING":
            raise HTTPException(status_code=404, detail="Pending request not found")
        
        if action == "APPROVE":
            self.leave_repo.update_request_status(request, "APPROVED_BY_HR")
            message = "Leave request forwarded to CEO for final approval"
        else:
            self.leave_repo.update_request_status(request, "REJECTED")
            message = "Leave request rejected by HR"
        
        # PERSIST REMARKS: Update the request object directly
        request.hr_remarks = remarks
        
        # Log approval action
        log_data = {
            "request_id": request_id,
            "approver_id": hr.emp_id,
            "action": action,
            "remarks": remarks
        }
        self.leave_repo.create_approval_log(log_data)
        
        # Notify applicant
        status_msg = "approved by HR and forwarded to CEO" if action == "APPROVE" else "rejected by HR"
        self.comm_service.notify_user(
            request.emp_id,
            f"Your leave request for {request.start_date} has been {status_msg}.",
            "LEAVE",
            "/leave-management"
        )
        
        if action == "APPROVE":
            # Notify CEO
            self.comm_service.notify_role(
                UserRole.CEO,
                f"New leave approval pending from {request.owner.full_name}",
                "LEAVE",
                "/leave-management"
            )

        self.leave_repo.commit()
        return {"message": message}
    
    def approve_by_ceo(self, request_id: int, ceo: Employee, action: str, remarks: str = None) -> Dict:
        """
        CEO final approval/rejection
        
        Args:
            request_id: Leave request ID
            ceo: CEO employee
            action: APPROVE or REJECT
            remarks: Optional remarks
            
        Returns:
            Success message
        """
        request = self.leave_repo.get_request_by_id(request_id)
        if not request or request.status != "APPROVED_BY_HR":
            raise HTTPException(status_code=404, detail="HR-approved request not found")
        
        if action == "APPROVE":
            self.leave_repo.update_request_status(request, "APPROVED")
            
            # Update balance
            year = request.start_date.year
            balance = self.leave_repo.get_balance(request.emp_id, request.leave_type_id, year)
            if balance:
                self.leave_repo.update_balance_used(balance, request.total_days)
            
            # Sync attendance
            self._sync_attendance_on_approval(request)
            message = "Leave request approved by CEO"
        else:
            self.leave_repo.update_request_status(request, "REJECTED")
            message = "Leave request rejected by CEO"
        
        # PERSIST REMARKS: Update the request object directly
        request.ceo_remarks = remarks
        
        # Log approval action
        log_data = {
            "request_id": request_id,
            "approver_id": ceo.emp_id,
            "action": action,
            "remarks": remarks
        }
        self.leave_repo.create_approval_log(log_data)
        
        # Notify applicant
        status_msg = "approved" if action == "APPROVE" else "rejected"
        self.comm_service.notify_user(
            request.emp_id,
            f"Your leave request for {request.start_date} has been {status_msg} by CEO.",
            "LEAVE",
            "/leave-management"
        )
        
        if action == "APPROVE":
             # Notify HR
            self.comm_service.notify_role(
                UserRole.HR,
                f"CEO has approved leave for {request.owner.full_name}",
                "LEAVE",
                "/leave-management"
            )

        self.leave_repo.commit()
        return {"message": message}
    
    def _validate_leave_dates(self, start_date: date, end_date: date) -> None:
        """Validate leave dates"""
        if start_date < date.today():
            raise HTTPException(status_code=400, detail="Cannot apply for leave in the past")
        
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date")
    
    def _calculate_work_days(self, start: date, end: date) -> int:
        """Calculate work days (excluding weekends and holidays)"""
        # Get holidays in this range
        holidays = self.leave_repo.get_holidays_in_range(start, end)
        holiday_dates = {h.date for h in holidays}
        
        days = 0
        curr = start
        while curr <= end:
            # Check if it's a weekday (including Saturday) AND not a holiday
            if curr.weekday() < 6 and curr not in holiday_dates:
                days += 1
            curr += timedelta(days=1)
        return days
    
    def _sync_attendance_on_approval(self, request) -> None:
        """Mark attendance as 'On Leave' for approved dates"""
        curr = request.start_date
        while curr <= request.end_date:
            if curr.weekday() < 6:
                existing = self.attendance_repo.get_by_emp_and_date(request.emp_id, curr)
                
                if existing:
                    self.attendance_repo.update(existing, {"attendance_status": "On Leave"})
                else:
                    attendance_data = {
                        "emp_id": request.emp_id,
                        "date": curr,
                        "attendance_status": "On Leave",
                        "source_file": "LEAVE_MODULE"
                    }
                    self.attendance_repo.create(attendance_data)
            
            curr += timedelta(days=1)

    def get_employee_summary(self, emp_id: str = None) -> Dict:
        """
        Get comprehensive leave summary for admin/HR
        
        Args:
            emp_id: Optional Employee ID. If None, returns top 5 recent requests.
            
        Returns:
            Dictionary with balances and request history
        """
        year = datetime.now().year
        
        if emp_id:
            employee = self.employee_repo.get_by_emp_id(emp_id)
            if not employee:
                raise HTTPException(status_code=404, detail=f"Employee with ID {emp_id} not found")
                
            balances = self.get_employee_balances(emp_id, year)
            requests = self.get_my_requests(emp_id)
            
            # Map employee to plain dict to avoid circular reference recursion
            employee_data = {
                "id": employee.id,
                "emp_id": employee.emp_id,
                "full_name": employee.full_name,
                "email": employee.email,
                "designation": employee.designation,
                "role": employee.role,
                "status": employee.status
            }
            
            return {
                "emp_id": emp_id,
                "employee": employee_data,
                "year": year,
                "balances": balances,
                "history": requests
            }
        else:
            # Default "Explorer" mode - show top 5 recent requests from anyone
            recent_requests = self.leave_repo.get_all_requests(limit=5)
            return {
                "emp_id": "ALL",
                "year": year,
                "history": recent_requests,
                "balances": [] # No specific balances in "All" view
            }

    # Holiday Management
    def add_holiday(self, holiday_data: dict) -> Dict:
        """Add new holiday"""
        h_date = holiday_data['date']
        if isinstance(h_date, str):
            # Take only the date part if it's an ISO string
            h_date = h_date.split('T')[0]
            h_date = datetime.strptime(h_date, '%Y-%m-%d').date()
        
        # Check if holiday exists on this date
        from app.models.models import Holiday
        existing = self.db.query(Holiday).filter(Holiday.date == h_date).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"A holiday already exists on {h_date} ({existing.name})")

        holiday_data['year'] = h_date.year
        holiday_data['day'] = h_date.strftime('%A')
        holiday_data['date'] = h_date
        
        self.leave_repo.create_holiday(holiday_data)
        try:
            self.leave_repo.commit()
            return {"message": f"Holiday {holiday_data['name']} added for {h_date}"}
        except Exception as e:
            self.leave_repo.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to add holiday: {str(e)}")

    def edit_holiday(self, holiday_id: int, holiday_data: dict) -> Dict:
        """Update existing holiday"""
        holiday = self.leave_repo.get_holiday_by_id(holiday_id)
        if not holiday:
            raise HTTPException(status_code=404, detail="Holiday not found")
        
        # Validate name if provided
        if 'name' in holiday_data and not holiday_data['name']:
            raise HTTPException(status_code=400, detail="Holiday name cannot be empty")

        if 'date' in holiday_data:
            h_date = holiday_data['date']
            if not h_date:
                raise HTTPException(status_code=400, detail="Holiday date cannot be empty")
                
            if isinstance(h_date, str):
                try:
                    h_date = h_date.split('T')[0]
                    h_date = datetime.strptime(h_date, '%Y-%m-%d').date()
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid date format: {h_date}. Expected YYYY-MM-DD")
            
            # Check for other holidays on this date
            from app.models.models import Holiday
            existing = self.db.query(Holiday).filter(Holiday.date == h_date, Holiday.id != holiday_id).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Another holiday already exists on {h_date} ({existing.name})")

            holiday_data['year'] = h_date.year
            holiday_data['day'] = h_date.strftime('%A')
            holiday_data['date'] = h_date

        self.leave_repo.update_holiday(holiday, holiday_data)
        try:
            self.leave_repo.commit()
            return {"message": "Holiday updated successfully"}
        except Exception as e:
            self.leave_repo.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update holiday: {str(e)}")

    def remove_holiday(self, holiday_id: int) -> Dict:
        """Delete a holiday"""
        holiday = self.leave_repo.get_holiday_by_id(holiday_id)
        if not holiday:
            raise HTTPException(status_code=404, detail="Holiday not found")
        
        self.leave_repo.delete_holiday(holiday)
        try:
            self.leave_repo.commit()
            return {"message": "Holiday deleted successfully"}
        except Exception as e:
            self.leave_repo.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete holiday: {str(e)}")
