from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime
import uuid

class NotificationBase(BaseModel):
    type: str
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: uuid.UUID

class NotificationResponse(NotificationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
