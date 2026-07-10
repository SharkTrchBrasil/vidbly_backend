from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database import Base


class CreatorService(Base):
    """Services offered by a creator with individual pricing.
    Maps to Billo's service types: Instagram Reel, TikTok post,
    Meta Partnership Ads, TikTok Spark Ads, etc."""
    __tablename__ = "creator_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    
    # Service identification (mirrors Billo's service IDs)
    service_type = Column(String, nullable=False)  # organic_post, partnership_ads, spark_ads
    platform = Column(String, nullable=False)       # instagram, tiktok, meta
    subtype = Column(String, nullable=True)          # content_level, account_level
    
    # Pricing (set by creator)
    price = Column(Float, nullable=False, default=0.0)
    
    # Active/Inactive toggle
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# Available platform services (reference data)
PLATFORM_SERVICES = [
    {"service_type": "organic_post", "platform": "instagram", "subtype": None, "label": "Instagram Reel"},
    {"service_type": "organic_post", "platform": "tiktok", "subtype": None, "label": "TikTok"},
    {"service_type": "partnership_ads", "platform": "meta", "subtype": "content_level", "label": "Meta Partnership Ads (Content-level)"},
    {"service_type": "partnership_ads", "platform": "meta", "subtype": "account_level", "label": "Meta Partnership Ads (Account-level)"},
    {"service_type": "spark_ads", "platform": "tiktok", "subtype": "content_level", "label": "TikTok Spark Ads (Content-level)"},
]
