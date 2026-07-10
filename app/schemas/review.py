from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    job_id: uuid.UUID
    reviewee_id: uuid.UUID

class ReviewResponse(ReviewBase):
    id: uuid.UUID
    job_id: uuid.UUID
    reviewer_id: uuid.UUID
    reviewee_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
