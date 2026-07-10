from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database import Base

class VideoRevision(Base):
    __tablename__ = "video_revisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("video_deliveries.id", ondelete="CASCADE"), nullable=False)
    feedback_text = Column(Text, nullable=False)
    status = Column(String(20), default="pending") # pending, resolved
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
