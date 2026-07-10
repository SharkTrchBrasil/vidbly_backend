from pydantic import BaseModel
from typing import Optional

class CreatorTagBase(BaseModel):
    category: str
    title: str

class CreatorTagResponse(CreatorTagBase):
    id: int

    class Config:
        from_attributes = True
