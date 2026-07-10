from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime


class CreatorServiceBase(BaseModel):
    service_type: str  # organic_post, partnership_ads, spark_ads
    platform: str      # instagram, tiktok, meta
    subtype: Optional[str] = None  # content_level, account_level
    price: float = 0.0
    is_active: Optional[bool] = True


class CreatorServiceCreate(CreatorServiceBase):
    pass


class CreatorServiceUpdate(BaseModel):
    price: Optional[float] = None
    is_active: Optional[bool] = None


class CreatorServiceResponse(CreatorServiceBase):
    id: UUID4
    creator_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
