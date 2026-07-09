from sqlalchemy import Column, String, ForeignKey, DateTime, DECIMAL, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    job_type = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    video_format = Column(String(10), nullable=False)
    video_duration_min = Column(Integer, default=15)
    video_duration_max = Column(Integer, default=60)
    budget_per_video = Column(DECIMAL(10, 2), nullable=False)
    platform_fee = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    max_creators = Column(Integer, default=1)
    accepted_creators = Column(Integer, default=0)
    requires_product = Column(Boolean, default=False)
    product_description = Column(Text)
    guidelines = Column(Text)
    max_revisions = Column(Integer, default=2)
    deadline_days = Column(Integer, default=7)
    status = Column(String(20), default='draft') # draft, open, in_progress, completed, cancelled
    efi_txid = Column(String(100))
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
