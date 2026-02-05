"""
Payroll Model
Contains payroll records
"""
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Date, ForeignKey, Unicode
from sqlalchemy.orm import relationship
from decimal import Decimal
import enum
from app.models.base import Base, get_ist_now

class PayrollStatus(str, enum.Enum):
    """Payroll status enumeration"""
    DRAFT = "DRAFT"
    PROCESSED = "PROCESSED"
    PAID = "PAID"

class PayrollRecord(Base):
    """Payroll Record model - represents monthly payroll for employees"""
    __tablename__ = "payroll_records"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Unicode(50), ForeignKey("employees.emp_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relationship to Employee
    owner = relationship("Employee", primaryjoin="PayrollRecord.emp_id == Employee.emp_id", foreign_keys=[emp_id], backref="payroll_records")
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    basic_salary = Column(DECIMAL(10, 2), nullable=False)
    hra = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    transport_allowance = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    dearness_allowance = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    medical_allowance = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    special_allowance = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    other_allowances = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    overtime_amount = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    gross_salary = Column(DECIMAL(10, 2), nullable=False)
    total_deductions = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    net_salary = Column(DECIMAL(10, 2), nullable=False)
    deduction_details = Column(String, nullable=True)  # JSON string
    working_days = Column(Integer, nullable=True)
    present_days = Column(Integer, nullable=True)
    absent_days = Column(Integer, nullable=True)
    overtime_hours = Column(DECIMAL(5, 2), default=Decimal('0.00'))
    status = Column(String(20), default="DRAFT")
    processed_at = Column(DateTime, nullable=True)
    processed_by = Column(String(50), nullable=True)
    payment_date = Column(Date, nullable=True)
    payment_method = Column(String(50), nullable=True)  # Bank Transfer, Cash, etc.
    remarks = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=get_ist_now)
