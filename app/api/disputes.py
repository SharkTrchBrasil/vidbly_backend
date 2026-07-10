from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..models.dispute import Dispute
from ..models.job import Job
from ..core.dependencies import get_current_active_user

router = APIRouter()

class DisputeCreate(BaseModel):
    job_id: str
    reason: str

@router.get("")
def get_disputes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    disputes = db.query(Dispute).filter(Dispute.opened_by_id == current_user.id).all()
    return disputes

@router.post("")
def create_dispute(
    dispute_data: DisputeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    job = db.query(Job).filter(Job.id == dispute_data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    dispute = Dispute(
        job_id=job.id,
        opened_by_id=current_user.id,
        reason=dispute_data.reason
    )
    db.add(dispute)
    db.commit()
    db.refresh(dispute)
    return dispute
