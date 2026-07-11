from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database import Base

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), nullable=False) # Can reference BrandWallet or CreatorWallet
    wallet_type = Column(String(20), nullable=False) # "brand" or "creator"
    
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False) # "credit" or "debit"
    description = Column(String, nullable=False)
    reference_id = Column(String, nullable=True) # E.g., job_id or payment_id
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)
    category = Column(String, nullable=True) # topup, job_charge, job_payout, refund, bonus
    status = Column(String(20), default="completed") # pending, completed, failed
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
