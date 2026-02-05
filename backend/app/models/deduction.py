"""
Deduction Models
Contains deduction types and employee deductions
"""
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, Date, ForeignKey, Unicode
from sqlalchemy.orm import relationship
from decimal import Decimal
import enum
from app.models.base import Base

class CalculationType(str, enum.Enum):
    """Calculation type enumeration"""
    FIXED = "FIXED"
    PERCENTAGE = "PERCENTAGE"

class DeductionType(Base):
    """Deduction Type model - represents types of deductions"""
    __tablename__ = "deduction_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    calculation_type = Column(String(20), nullable=False)
    default_value = Column(DECIMAL(10, 2), nullable=True)
    is_mandatory = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

class EmployeeDeduction(Base):
    """Employee Deduction model - represents employee-specific deductions"""
    __tablename__ = "employee_deductions"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Unicode(50), ForeignKey("employees.emp_id", ondelete="CASCADE"), nullable=False, index=True)
    deduction_type_id = Column(Integer, ForeignKey("deduction_types.id"), nullable=False)
    
    # Relationships
    owner = relationship("Employee", primaryjoin="EmployeeDeduction.emp_id == Employee.emp_id", foreign_keys=[emp_id], backref="deductions")
    deduction_type = relationship("DeductionType")
    calculation_type = Column(String(20), nullable=False)
    value = Column(DECIMAL(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
