from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..database import Base

class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    company_name = Column(String(200), nullable=False)
    logo_url = Column(String(500))
    website = Column(String(500))
    instagram = Column(String(100))
    segment = Column(String(100))
    cnpj = Column(String(18))
    contact_name = Column(String(200))
    contact_phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
