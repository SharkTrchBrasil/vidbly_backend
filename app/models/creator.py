from sqlalchemy import Column, String, ForeignKey, DateTime, DECIMAL, Integer, Boolean, Text, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from ..database import Base

class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500))
    pitch_video_url = Column(String(500), nullable=True) # First video uploaded during onboarding
    bio = Column(Text)
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    phone = Column(String(20))
    email_public = Column(String(255))
    cpf = Column(String(14))
    instagram = Column(String(100))
    tiktok = Column(String(100))
    youtube = Column(String(100))
    city = Column(String(100))
    state = Column(String(2))
    categories = Column(ARRAY(String))
    languages = Column(ARRAY(String))
    portfolio_urls = Column(ARRAY(String))
    rating = Column(Float, default=5.0)
    completed_jobs = Column(Integer, default=0)
    on_time_delivery_percentage = Column(Integer, default=100)
    premium_status = Column(String, nullable=True)
    country_code = Column(Integer, nullable=True)
    favorited_by_brand = Column(Boolean, default=False)
    invited = Column(Boolean, default=False)
    match_count = Column(Integer, default=0)
    occupation = Column(String, nullable=True)
    delivery_time_average_days = Column(Float, nullable=True)
    ranked_slots_count = Column(Integer, nullable=True)
    preferred_currency = Column(String, default="BRL")
    performance_ctr = Column(Float, nullable=True)
    performance_hook_rate = Column(Float, nullable=True)
    performance_roas = Column(Float, nullable=True)
    
    # Social/Organic metrics (for Billo-style filters)
    followers_count = Column(Integer, nullable=True)
    views_per_reel = Column(Integer, nullable=True)
    organic_post_price = Column(Float, nullable=True)
    cost_per_view = Column(Float, nullable=True)
    partnership_ads_price = Column(Float, nullable=True)
    hourly_rate = Column(DECIMAL(10, 2))
    total_earned = Column(DECIMAL(12, 2), default=0.0)
    response_time_hours = Column(Integer)
    availability_status = Column(String(20), default="available")
    is_approved = Column(Boolean, default=False)
    stripe_account_id = Column(String, nullable=True)
    stripe_account_status = Column(String, default="pending")
    stripe_onboarding_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
