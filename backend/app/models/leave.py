"""
Leave Models
Contains all leave management related models
"""
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime, Unicode
from sqlalchemy.orm import relationship, backref
from app.models.base import Base, get_ist_now

class LeaveType(Base):
    """Leave type model - defines types of leaves (All leaves are PAID)"""
    __tablename__ = "leave_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    annual_quota = Column(Integer, default=20)
    is_paid = Column(Boolean, default=True, nullable=False)  # Always True - only paid leave allowed
    allow_carry_forward = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

class LeaveBalance(Base):
    """Leave balance model - tracks employee leave balances"""
    __tablename__ = "leave_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Unicode(50), ForeignKey("employees.emp_id", ondelete="CASCADE"), index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id", ondelete="CASCADE"))
    
    # Relationship to Employee
    owner = relationship("Employee", primaryjoin="LeaveBalance.emp_id == Employee.emp_id", foreign_keys=[emp_id], backref=backref("leave_balances", cascade="all, delete-orphan"))
    year = Column(Integer, index=True)
    allocated = Column(Integer)
    used = Column(Integer, default=0)

class LeaveRequest(Base):
    """Leave request model - employee leave applications"""
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Unicode(50), ForeignKey("employees.emp_id", ondelete="CASCADE"), index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id", ondelete="CASCADE"))

    # Relationships
    owner = relationship("Employee", primaryjoin="LeaveRequest.emp_id == Employee.emp_id", foreign_keys=[emp_id], backref=backref("leave_requests", cascade="all, delete-orphan"))
    leave_type = relationship("LeaveType")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Integer)
    reason = Column(String(500))
    status = Column(String(20), default="PENDING")  # PENDING, APPROVED_BY_HR, APPROVED, REJECTED
    hr_remarks = Column(String(500), nullable=True)
    ceo_remarks = Column(String(500), nullable=True)
    attachment_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=get_ist_now)

class LeaveApprovalLog(Base):
    """Leave approval log model - tracks approval actions"""
    __tablename__ = "leave_approval_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("leave_requests.id", ondelete="CASCADE"))
    
    # Relationship to LeaveRequest
    request = relationship("LeaveRequest", backref=backref("approval_logs", cascade="all, delete-orphan"))
    
    approver_id = Column(Unicode(50), ForeignKey("employees.emp_id", ondelete="NO ACTION"), nullable=True)
    
    # Relationship to Approver
    approver = relationship("Employee", primaryjoin="LeaveApprovalLog.approver_id == Employee.emp_id", foreign_keys=[approver_id], backref=backref("approvals_given", cascade="all, delete-orphan"))
    
    action = Column(String(20))  # HR_APPROVED, CEO_APPROVED, REJECTED
    remarks = Column(String(500), nullable=True)
    action_at = Column(DateTime, default=get_ist_now)

class Holiday(Base):
    """Holiday model - list of public holidays"""
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    date = Column(Date, nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    day = Column(String(20), nullable=True) # e.g. "Monday"
