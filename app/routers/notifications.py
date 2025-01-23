from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Notification
from app.schemas import NotificationCreate, NotificationOut, MarkReadRequest, DeleteNotificationRequest
from app.dependencies import get_db
from typing import Optional, Dict, Any
from fastapi import status


router = APIRouter()


@router.post("/", response_model=NotificationOut)
async def create_notification(notification: NotificationCreate, db: AsyncSession = Depends(get_db)):
    new_notification = Notification(**notification.dict())
    db.add(new_notification)
    await db.commit()
    await db.refresh(new_notification)
    return new_notification


@router.get("/", response_model=Dict[str, Any])
async def get_notifications(
    user_id: Optional[int] = Query(None),
    search_text: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    # Base query: Filter out deleted notifications
    query = select(Notification).where(Notification.deleted_at.is_(None))

    # Apply user_id filter
    if user_id:
        query = query.filter(Notification.user_id == user_id)

    # Apply search_text filter
    if search_text:
        query = query.filter(
            Notification.title.ilike(f"%{search_text}%") | Notification.content.ilike(f"%{search_text}%")
        )

    # Execute query to get total count of matching notifications
    count_query = query.with_only_columns(func.count())  # Count total rows
    result = await db.execute(count_query)
    total_count = result.scalar() or 0

    # Paginate the query
    paginated_query = query.offset((page - 1) * page_size).limit(page_size)
    paginated_result = await db.execute(paginated_query)
    notifications = paginated_result.scalars().all()

    # Serialize results with Pydantic
    serialized_notifications = [NotificationOut.from_orm(notification) for notification in notifications]

    # Build the simplified response
    response = {
        "count": total_count,
        "data": serialized_notifications
    }

    return response


@router.put("/mark-read", status_code=status.HTTP_200_OK)
async def mark_notifications_read(
    request: MarkReadRequest,
    db: AsyncSession = Depends(get_db),
):
    # Validate input
    if not request.mark_all and not request.notification_ids:
        raise HTTPException(
            status_code=400,
            detail="Either notification_ids or mark_all flag must be provided"
        )

    query = select(Notification).where(
        Notification.user_id == request.user_id,
        Notification.deleted_at.is_(None)
    )

    if request.mark_all:
        query = query
    else:
        query = query.where(Notification.id.in_(request.notification_ids))

    result = await db.execute(query)
    notifications = result.scalars().all()

    if not notifications:
        raise HTTPException(status_code=404, detail="No matching notifications found")

    for notification in notifications:
        notification.read_at = datetime.utcnow() if request.read else None
        db.add(notification)

    await db.commit()

    return {
        "detail": f"{len(notifications)} notifications marked as {'read' if request.read else 'unread'}"
    }


@router.put("/{notification_id}", status_code=status.HTTP_200_OK)
async def delete_notification(
    notification_id: int,
    request: DeleteNotificationRequest,
    db: AsyncSession = Depends(get_db)
):
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == request.user_id,
        Notification.deleted_at.is_(None)
    )
    result = await db.execute(query)
    db_notification = result.scalars().first()

    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found or unauthorized access")

    db_notification.deleted_at = datetime.utcnow()
    db.add(db_notification)
    await db.commit()

    return {"detail": "Notification deleted successfully"}


@router.get("/unread/count", status_code=status.HTTP_200_OK)
async def get_unread_notification_count(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = select(func.count()).where(
        Notification.user_id == user_id,
        Notification.read_at.is_(None),
        Notification.deleted_at.is_(None)
    )
    result = await db.execute(query)
    unread_count = result.scalar() or 0

    return {"unread_count": unread_count}
