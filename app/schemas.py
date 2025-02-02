import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    content: str
    notification_metadata: Optional[Dict[str, Any]] = None  # Metadata is optional


class NotificationOut(NotificationCreate):
    id: uuid.UUID
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        orm_mode = True
        from_attributes = True


class MarkReadRequest(BaseModel):
    user_id: int
    notification_ids: Optional[List[int]] = None
    mark_all: Optional[bool] = False
    read: bool


class DeleteNotificationRequest(BaseModel):
    user_id: int
