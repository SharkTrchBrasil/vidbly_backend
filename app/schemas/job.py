from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class JobBase(BaseModel):
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    job_type: str
    category: str
    target_platform: Optional[str] = None
    language: Optional[str] = "pt-BR"
    video_format: str
    video_duration_min: int = 15
    video_duration_max: int = 60
    budget_per_video: float
    max_creators: int = 1
    requires_product: bool = False
    product_description: Optional[str] = None
    guidelines: Optional[str] = None
    script_required: bool = False
    script_text: Optional[str] = None
    reference_urls: Optional[list[str]] = []
    
    pricing_tier: str
    addon_express_delivery: bool = False
    addon_pro_editing: bool = False
    addon_premium_creator: bool = False
    addon_extra_revisions: bool = False
    addon_extended_rights: bool = False
    
    max_revisions: int = 2
    deadline_days: int = 7
    expires_at: Optional[datetime] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    job_type: Optional[str] = None
    category: Optional[str] = None
    target_platform: Optional[str] = None
    language: Optional[str] = None
    video_format: Optional[str] = None
    video_duration_min: Optional[int] = None
    video_duration_max: Optional[int] = None
    budget_per_video: Optional[float] = None
    max_creators: Optional[int] = None
    requires_product: Optional[bool] = None
    product_description: Optional[str] = None
    product_id: Optional[UUID4] = None
    
    # Billo fields
    editing_services: Optional[str] = None
    access_level: Optional[str] = None
    target_countries: Optional[str] = None
    campaign_type: Optional[str] = None
    brief_persona: Optional[str] = None
    creator_services: Optional[str] = None
    invitations_cap: Optional[int] = None
    services: Optional[str] = None
    
    guidelines: Optional[str] = None
    script_required: Optional[bool] = None
    script_text: Optional[str] = None
    reference_urls: Optional[list[str]] = None
    
    pricing_tier: Optional[str] = None
    addon_express_delivery: Optional[bool] = None
    addon_pro_editing: Optional[bool] = None
    addon_premium_creator: Optional[bool] = None
    addon_extra_revisions: Optional[bool] = None
    addon_extended_rights: Optional[bool] = None
    
    max_revisions: Optional[int] = None
    deadline_days: Optional[int] = None
    expires_at: Optional[datetime] = None

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
