from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class VideoDeliveryBase(BaseModel):
    s3_key: str

class VideoDeliveryCreate(VideoDeliveryBase):
    job_id: uuid.UUID

class VideoDeliveryUpdate(BaseModel):
    status: str

class VideoDeliveryResponse(VideoDeliveryBase):
    id: uuid.UUID
    job_id: uuid.UUID
    creator_id: uuid.UUID
    status: str
    revision_count: int
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
