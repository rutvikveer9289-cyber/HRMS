"""
Employee Document Model
Tracks documents uploaded for employees
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Unicode
from sqlalchemy.orm import relationship
from app.models.base import Base, get_ist_now

class EmployeeDocument(Base):
    """Model for storing employee document metadata and paths"""
    __tablename__ = "employee_documents"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Unicode(50), ForeignKey("employees.emp_id", ondelete="CASCADE"), index=True)
    document_type = Column(String(100)) # id_proof, address_proof, education, experience
    document_name = Column(String(200)) # Friendly name
    file_name = Column(String(255)) # Actual file name on disk
    file_path = Column(String(500)) # Full path to file
    uploaded_at = Column(DateTime, default=get_ist_now)

    # Relationship to employee
    owner = relationship("Employee", back_populates="documents")
