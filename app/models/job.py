from sqlalchemy import Column, String, ForeignKey, DateTime, DECIMAL, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone
import uuid
from ..database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    thumbnail_url = Column(String(500))
    job_type = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    target_platform = Column(String(50))
    language = Column(String(10), default="pt-BR")
    video_format = Column(String(10), nullable=False)
    video_duration_min = Column(Integer, default=15)
    video_duration_max = Column(Integer, default=60)
    budget_per_video = Column(DECIMAL(10, 2), nullable=False)
    platform_fee = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    max_creators = Column(Integer, default=1)
    video_format = Column(String, nullable=False) # 9:16, 16:9
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    
    # Billo fields
    editing_services = Column(String, nullable=True) # None, Captions, Expert
    access_level = Column(String, default="public")
    target_countries = Column(String, nullable=True)
    campaign_type = Column(String, default="videoAd")
    brief_persona = Column(String, nullable=True)
    creator_services = Column(String, nullable=True)
    invitations_cap = Column(Integer, nullable=True)
    services = Column(String, nullable=True)
    product_description = Column(Text)
    guidelines = Column(Text)
    script_required = Column(Boolean, default=False)
    script_text = Column(Text)
    reference_urls = Column(ARRAY(String))
    
    accepted_creators = Column(Integer, default=0)
    requires_product = Column(Boolean, default=False)
    
    # New Pricing & Add-on fields
    pricing_tier = Column(String(50), nullable=False) # depoimento, unboxing, review, premium, pack
    addon_express_delivery = Column(Boolean, default=False)
    addon_pro_editing = Column(Boolean, default=False)
    addon_premium_creator = Column(Boolean, default=False)
    addon_extra_revisions = Column(Boolean, default=False)
    addon_extended_rights = Column(Boolean, default=False)
    
    max_revisions = Column(Integer, default=2)
    deadline_days = Column(Integer, default=7)
    expires_at = Column(DateTime)
    status = Column(String(20), default='draft') # draft, open, in_progress, completed, cancelled
    efi_txid = Column(String(100))
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
