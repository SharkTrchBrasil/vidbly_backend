from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class JobBase(BaseModel):
    title: str
    description: str
    job_type: str
    category: str
    video_format: str
    video_duration_min: int = 15
    video_duration_max: int = 60
    budget_per_video: float
    max_creators: int = 1
    requires_product: bool = False
    product_description: Optional[str] = None
    guidelines: Optional[str] = None
    max_revisions: int = 2
    deadline_days: int = 7

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[str] = None
    category: Optional[str] = None
    video_format: Optional[str] = None
    video_duration_min: Optional[int] = None
    video_duration_max: Optional[int] = None
    budget_per_video: Optional[float] = None
    max_creators: Optional[int] = None
    requires_product: Optional[bool] = None
    product_description: Optional[str] = None
    guidelines: Optional[str] = None
    max_revisions: Optional[int] = None
    deadline_days: Optional[int] = None

class JobResponse(JobBase):
    id: uuid.UUID
    brand_id: uuid.UUID
    platform_fee: float
    total_price: float
    accepted_creators: int
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
