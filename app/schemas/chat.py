from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class ChatMessageBase(BaseModel):
    message: str
    message_type: Optional[str] = "text"
    is_read: Optional[bool] = False

class ChatMessageCreate(ChatMessageBase):
    job_id: UUID4
    receiver_id: UUID4

class ChatMessageResponse(ChatMessageBase):
    id: UUID4
    job_id: UUID4
    sender_id: UUID4
    receiver_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True
