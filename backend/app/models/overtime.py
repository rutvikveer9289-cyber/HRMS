"""
Overtime Model
Contains overtime tracking records
"""
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Date, ForeignKey, Unicode
from sqlalchemy.orm import relationship, backref
from decimal import Decimal
import enum
from app.models.base import Base, get_ist_now

class OvertimeStatus(str, enum.Enum):
    """Overtime status enumeration"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class OvertimeRecord(Base):
    """Overtime Record model - tracks employee overtime"""
    __tablename__ = "overtime_records"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Unicode(50), ForeignKey("employees.emp_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relationship to Employee
    owner = relationship("Employee", primaryjoin="OvertimeRecord.emp_id == Employee.emp_id", foreign_keys=[emp_id], backref=backref("overtime_records", cascade="all, delete-orphan"))
    date = Column(Date, nullable=False, index=True)
    regular_hours = Column(DECIMAL(5, 2), default=Decimal('8.00'))
    actual_hours = Column(DECIMAL(5, 2), nullable=False)
    overtime_hours = Column(DECIMAL(5, 2), nullable=False)
    overtime_rate = Column(DECIMAL(5, 2), default=Decimal('1.50'))
    overtime_amount = Column(DECIMAL(10, 2), nullable=True)
    status = Column(String(20), default="PENDING")
    approved_by = Column(String(50), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    remarks = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=get_ist_now)
