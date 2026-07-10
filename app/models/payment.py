from sqlalchemy import Column, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default="BRL")
    provider = Column(String(20), nullable=False) # stripe
    provider_txid = Column(String(255))
    status = Column(String(20), default="pending") # pending, completed, failed, refunded
    payment_type = Column(String(20), nullable=False) # charge, payout
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
