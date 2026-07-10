from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
import uuid

class BrandProfileBase(BaseModel):
    company_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    instagram: Optional[str] = None
    segment: Optional[str] = None
    cnpj: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None

    # Billo fields
    color: Optional[str] = None
    core_message: Optional[str] = None
    country_code: Optional[int] = None
    currency: Optional[str] = "BRL"
    days_to_approve_content: Optional[int] = 3
    watermark_url: Optional[str] = None
    cover_picture_url: Optional[str] = None
    business_type: Optional[str] = None
    lead_source: Optional[str] = None
    icp: Optional[str] = None
    facebook_url: Optional[str] = None

class BrandProfileCreate(BrandProfileBase):
    pass

class BrandProfileUpdate(BrandProfileBase):
    company_name: Optional[str] = None

class BrandProfileResponse(BrandProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    plan_type: str
    total_spent: float
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
