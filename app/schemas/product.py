from pydantic import BaseModel, UUID4, AnyHttpUrl
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    product_url: Optional[str] = None
    photo_url: Optional[str] = None
    product_type: Optional[str] = "physical"
    requires_shipping: Optional[bool] = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None

class ProductResponse(ProductBase):
    id: UUID4
    brand_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
