from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.api.dependencies import get_db, get_current_user, check_admin
from app.services.communication_service import CommunicationService
from app.models.models import Employee

router = APIRouter()

class AnnouncementCreate(BaseModel):
    title: str
    content: str

# Announcement Endpoints
@router.get("/announcements")
def get_announcements(db: Session = Depends(get_db)):
    service = CommunicationService(db)
    return service.get_announcements()

@router.post("/announcements")
def create_announcement(
    data: AnnouncementCreate,
    admin: Employee = Depends(check_admin),
    db: Session = Depends(get_db)
):
    service = CommunicationService(db)
    return service.add_announcement(data.title, data.content, admin)

@router.delete("/announcements/{id}")
def delete_announcement(
    id: int,
    admin: Employee = Depends(check_admin),
    db: Session = Depends(get_db)
):
    service = CommunicationService(db)
    return service.remove_announcement(id, admin)

# Notification Endpoints
@router.get("/notifications")
def get_notifications(
    user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CommunicationService(db)
    return service.get_my_notifications(user)

@router.put("/notifications/{id}/read")
def mark_notification_read(
    id: int,
    user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CommunicationService(db)
    return service.mark_read(id, user)

@router.put("/notifications/read-all")
def mark_all_notifications_read(
    user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CommunicationService(db)
    return service.mark_all_read(user)

@router.delete("/notifications/{id}")
def delete_notification(
    id: int,
    user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CommunicationService(db)
    return service.remove_notification(id, user)

@router.delete("/notifications/clear-all")
def clear_all_notifications(
    user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CommunicationService(db)
    return service.clear_my_notifications(user)
