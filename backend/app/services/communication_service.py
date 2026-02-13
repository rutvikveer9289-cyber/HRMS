from sqlalchemy.orm import Session
from app.repositories.communication_repository import CommunicationRepository
from app.models.models import Employee, UserRole
from typing import List, Dict

class CommunicationService:
    def __init__(self, db: Session):
        self.repo = CommunicationRepository(db)

    def add_announcement(self, title: str, content: str, author: Employee) -> Dict:
        # Only Admin/HR/CEO can post announcements
        if author.role not in [UserRole.SUPER_ADMIN, UserRole.HR, UserRole.CEO]:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Not authorized to post announcements")
        
        data = {
            "title": title,
            "content": content,
            "author_id": author.emp_id
        }
        announcement = self.repo.create_announcement(data)
        
        # Also create a notification for everyone!
        self.create_broadcast_notification(
            f"New Announcement: {title}",
            "ANNOUNCEMENT",
            "/dashboard"
        )
        
        return {"message": "Announcement posted", "id": announcement.id}

    def get_announcements(self) -> List:
        return self.repo.get_active_announcements()

    def remove_announcement(self, announcement_id: int, user: Employee):
        if user.role not in [UserRole.SUPER_ADMIN, UserRole.HR, UserRole.CEO]:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if self.repo.delete_announcement(announcement_id):
            return {"message": "Announcement deleted"}
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Announcement not found")

    # Notifications
    def notify_user(self, emp_id: str, message: str, type: str = "SYSTEM", link: str = None):
        data = {
            "recipient_id": emp_id,
            "message": message,
            "type": type,
            "link": link
        }
        return self.repo.create_notification(data)

    def create_broadcast_notification(self, message: str, type: str = "SYSTEM", link: str = None):
        """Create a notification for every employee in the system"""
        # We need the employee list
        from app.models.models import Employee
        employees = self.repo.db.query(Employee).all()
        
        for emp in employees:
            data = {
                "recipient_id": emp.emp_id,
                "message": message,
                "type": type,
                "link": link
            }
            self.repo.create_notification(data)
        
        return {"message": f"Broadcast sent to {len(employees)} employees"}

    def get_my_notifications(self, user: Employee):
        return self.repo.get_user_notifications(user.emp_id)

    def mark_read(self, notification_id: int, user: Employee):
        return self.repo.mark_as_read(notification_id, user.emp_id)

    def mark_all_read(self, user: Employee):
        self.repo.mark_all_as_read(user.emp_id)
        return {"message": "All marked as read"}

    def remove_notification(self, notification_id: int, user: Employee):
        if self.repo.delete_notification(notification_id, user.emp_id):
            return {"message": "Notification removed"}
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")

    def clear_my_notifications(self, user: Employee):
        self.repo.clear_all_notifications(user.emp_id)
        return {"message": "Notification center cleared"}

    def notify_role(self, role: str, message: str, type: str = "SYSTEM", link: str = None):
        """Notify all users with a specific role"""
        from app.models.models import Employee
        users = self.repo.db.query(Employee).filter(Employee.role == role).all()
        for user in users:
            self.notify_user(user.emp_id, message, type, link)
