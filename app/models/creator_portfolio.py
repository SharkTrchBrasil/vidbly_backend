from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database import Base

class CreatorPortfolioItem(Base):
    __tablename__ = "creator_portfolio_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(200), nullable=False)
    video_url = Column(String(500), nullable=False) # Usually an S3 key or full URL
    thumbnail_url = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    
    views_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
