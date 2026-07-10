from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class VideoRevisionBase(BaseModel):
    feedback_text: str

class VideoRevisionCreate(VideoRevisionBase):
    delivery_id: uuid.UUID

class VideoRevisionResponse(VideoRevisionBase):
    id: uuid.UUID
    delivery_id: uuid.UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
