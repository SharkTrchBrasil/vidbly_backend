from sqlalchemy import Column, String, ForeignKey, DateTime, DECIMAL, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
from ..database import Base

class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500))
    bio = Column(String)
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    phone = Column(String(20))
    cpf = Column(String(14))
    instagram = Column(String(100))
    tiktok = Column(String(100))
    city = Column(String(100))
    state = Column(String(2))
    categories = Column(ARRAY(String))
    languages = Column(ARRAY(String))
    portfolio_urls = Column(ARRAY(String))
    rating = Column(DECIMAL(3, 2), default=0)
    completed_jobs = Column(Integer, default=0)
    is_approved = Column(Boolean, default=False)
    pix_key = Column(String(255))
    pix_key_type = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
