from sqlalchemy import Column, Float, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database import Base

class CreatorWallet(Base):
    __tablename__ = "creator_wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    available_balance = Column(Float, default=0.0)
    pending_balance = Column(Float, default=0.0)
    total_earned = Column(Float, default=0.0)
    
    bank_info = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
