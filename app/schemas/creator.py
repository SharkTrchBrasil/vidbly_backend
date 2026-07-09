from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime, date
import uuid

class CreatorProfileBase(BaseModel):
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    categories: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    portfolio_urls: Optional[List[str]] = []
    pix_key: Optional[str] = None
    pix_key_type: Optional[str] = None

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
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
