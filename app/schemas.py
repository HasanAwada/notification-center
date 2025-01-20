from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    content: str


class NotificationOut(NotificationCreate):
    id: int
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        orm_mode = True
