"""
Salary Structure Model
Contains salary structure and related enums
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Date, ForeignKey, Unicode
from sqlalchemy.orm import relationship, backref
from decimal import Decimal
import enum
from app.models.base import Base, get_ist_now

class SalaryStructure(Base):
    """Salary Structure model - represents employee salary components"""
    __tablename__ = "salary_structures"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Unicode(50), ForeignKey("employees.emp_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relationship to Employee
    owner = relationship("Employee", primaryjoin="SalaryStructure.emp_id == Employee.emp_id", foreign_keys=[emp_id], backref=backref("salary_structures", cascade="all, delete-orphan"))
    basic_salary = Column(DECIMAL(10, 2), nullable=False)
    hra = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    transport_allowance = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    dearness_allowance = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    medical_allowance = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    special_allowance = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    other_allowances = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    gross_salary = Column(DECIMAL(10, 2), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_ist_now)
    created_by = Column(String(50), nullable=True)
