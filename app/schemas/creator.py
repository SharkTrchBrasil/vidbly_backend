from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime, date
import uuid

class CreatorProfileBase(BaseModel):
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    pitch_video_url: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email_public: Optional[str] = None
    cpf: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    youtube: Optional[str] = None
    bio: Optional[str] = None
    categories: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    portfolio_urls: Optional[List[str]] = None
    hourly_rate: Optional[float] = None
    response_time_hours: Optional[int] = None
    
    # Billo fields
    on_time_delivery_percentage: Optional[int] = 100
    premium_status: Optional[str] = None
    country_code: Optional[int] = None
    favorited_by_brand: Optional[bool] = False
    invited: Optional[bool] = False
    match_count: Optional[int] = 0
    occupation: Optional[str] = None
    delivery_time_average_days: Optional[float] = None
    ranked_slots_count: Optional[int] = None
    preferred_currency: Optional[str] = "BRL"
    performance_ctr: Optional[float] = None
    performance_hook_rate: Optional[float] = None
    performance_roas: Optional[float] = None
    
    # Social/Organic metrics
    followers_count: Optional[int] = None
    views_per_reel: Optional[int] = None
    organic_post_price: Optional[float] = None
    cost_per_view: Optional[float] = None
    partnership_ads_price: Optional[float] = None
    
    availability_status: Optional[str] = "available"
    city: Optional[str] = None
    state: Optional[str] = None

class CreatorProfileCreate(CreatorProfileBase):
    pass

class CreatorProfileUpdate(CreatorProfileBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class CreatorProfileResponse(CreatorProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    rating: float
    completed_jobs: int
    total_earned: float
    stripe_account_id: Optional[str] = None
    stripe_account_status: Optional[str] = "pending"
    stripe_onboarding_complete: Optional[bool] = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
