from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class WalletBase(BaseModel):
    balance: Optional[float] = 0.0
    bonus_balance: Optional[float] = 0.0
    plan_type: Optional[str] = None

class WalletResponse(WalletBase):
    id: UUID4
    brand_id: UUID4
    last_topup_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
