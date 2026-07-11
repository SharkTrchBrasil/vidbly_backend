from sqlalchemy import Column, String, ForeignKey, DateTime, Text, DECIMAL, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database import Base

class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    company_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    logo_url = Column(String(500))
    website = Column(String(500))
    instagram = Column(String(100))
    segment = Column(String(100))
    cnpj = Column(String(18))
    address = Column(Text)
    contact_name = Column(String(200))
    contact_phone = Column(String(20))
    plan_type = Column(String(20), default="free")
    total_spent = Column(DECIMAL(12, 2), default=0.0)
    is_verified = Column(Boolean, default=False)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
