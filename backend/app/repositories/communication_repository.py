from sqlalchemy.orm import Session
from app.models.communication import Announcement, Notification
from typing import List, Optional
from datetime import datetime

class CommunicationRepository:
    def __init__(self, db: Session):
        self.db = db

    # Announcement Operations
    def create_announcement(self, data: dict) -> Announcement:
        announcement = Announcement(**data)
        self.db.add(announcement)
        self.db.commit()
        self.db.refresh(announcement)
        return announcement

    def get_active_announcements(self) -> List[Announcement]:
        return self.db.query(Announcement).filter(
            Announcement.is_active == True
        ).order_by(Announcement.created_at.desc()).all()

    def delete_announcement(self, announcement_id: int):
        announcement = self.db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if announcement:
            self.db.delete(announcement)
            self.db.commit()
            return True
        return False

    # Notification Operations
    def create_notification(self, data: dict) -> Notification:
        notification = Notification(**data)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_user_notifications(self, emp_id: str, limit: int = 20) -> List[Notification]:
        # Only get unread notifications to keep the action center clean
        return self.db.query(Notification).filter(
            Notification.recipient_id == emp_id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_as_read(self, notification_id: int, emp_id: str):
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.recipient_id == emp_id
        ).first()
        if notification:
            notification.is_read = True
            self.db.commit()
            return True
        return False

    def mark_all_as_read(self, emp_id: str):
        self.db.query(Notification).filter(
            Notification.recipient_id == emp_id,
            Notification.is_read == False
        ).update({"is_read": True}, synchronize_session=False)
        self.db.commit()

    def delete_notification(self, notification_id: int, emp_id: str):
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.recipient_id == emp_id
        ).first()
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        return False

    def clear_all_notifications(self, emp_id: str):
        self.db.query(Notification).filter(
            Notification.recipient_id == emp_id
        ).delete(synchronize_session=False)
        self.db.commit()
