from sqlalchemy import Column, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database import Base

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    brand_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    last_message_at = Column(DateTime, nullable=True)
    unread_count_brand = Column(Integer, default=0)
    unread_count_creator = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
