from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Notification
from app.schemas import NotificationCreate, NotificationOut
from app.dependencies import get_db
from typing import List, Optional
from fastapi import status

router = APIRouter()


@router.post("/", response_model=NotificationOut)
async def create_notification(notification: NotificationCreate, db: AsyncSession = Depends(get_db)):
    new_notification = Notification(**notification.dict())
    db.add(new_notification)
    await db.commit()
    await db.refresh(new_notification)
    return new_notification


@router.get("/", response_model=List[NotificationOut])
async def get_notifications(
    user_id: Optional[int] = Query(None),
    search_text: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Notification).where(Notification.deleted_at.is_(None))

    if user_id:
        query = query.filter(Notification.user_id == user_id)
    if search_text:
        query = query.filter(
            Notification.title.ilike(f"%{search_text}%") | Notification.content.ilike(f"%{search_text}%")
        )

    result = await db.execute(query)
    notifications = result.scalars().all()

    return notifications


@router.put("/{notification_id}/read", status_code=status.HTTP_200_OK, response_model=NotificationOut)
async def mark_notification_read(notification_id: int, read: bool, db: AsyncSession = Depends(get_db)):
    db_notification = await db.get(Notification, notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db_notification.read_at = datetime.utcnow() if read else None
    db.add(db_notification)
    await db.commit()
    await db.refresh(db_notification)
    return db_notification


@router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
async def delete_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    db_notification = await db.get(Notification, notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db_notification.deleted_at = datetime.utcnow()
    db.add(db_notification)
    await db.commit()
    return {"detail": "Notification soft deleted successfully"}
