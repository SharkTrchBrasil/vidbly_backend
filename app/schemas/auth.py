from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    user_type: str # 'creator' or 'brand'

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    
class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    user_type: str
    is_active: bool
    
    class Config:
        from_attributes = True
