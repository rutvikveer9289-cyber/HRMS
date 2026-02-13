"""
Communication Models
Contains Announcements and Notifications
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Unicode
from sqlalchemy.orm import relationship
from app.models.base import Base, get_ist_now

class Announcement(Base):
    """Company announcements shown on dashboard"""
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Unicode(50), ForeignKey("employees.emp_id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=get_ist_now)
    is_active = Column(Boolean, default=True)
    
    # Relationship
    author = relationship("Employee", primaryjoin="Announcement.author_id == Employee.emp_id")

class Notification(Base):
    """User notifications for the Action Center"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Unicode(50), ForeignKey("employees.emp_id", ondelete="CASCADE"), nullable=True) # Null means "Broadcast"
    message = Column(String(500), nullable=False)
    type = Column(String(50)) # LEAVE, ANNOUNCEMENT, SYSTEM
    link = Column(String(200), nullable=True) # Direct link to action (e.g. /leave-management)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_ist_now)
    
    # Relationship
    recipient = relationship("Employee", primaryjoin="Notification.recipient_id == Employee.emp_id")
