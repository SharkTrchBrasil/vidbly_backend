from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class JobApplicationBase(BaseModel):
    cover_letter: Optional[str] = None
    proposed_rate: Optional[float] = None

class JobApplicationCreate(JobApplicationBase):
    job_id: uuid.UUID

class JobApplicationUpdate(BaseModel):
    status: str

class JobApplicationResponse(JobApplicationBase):
    id: uuid.UUID
    job_id: uuid.UUID
    creator_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
