from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brand_profiles.id", ondelete="CASCADE"), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
