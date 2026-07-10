from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class PaymentBase(BaseModel):
    amount: float
    currency: Optional[str] = "BRL"
    provider: str
    payment_type: str

class PaymentCreate(PaymentBase):
    job_id: Optional[uuid.UUID] = None

class PaymentResponse(PaymentBase):
    id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    provider_txid: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
