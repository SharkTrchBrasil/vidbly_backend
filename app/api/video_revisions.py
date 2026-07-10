from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..database import get_db
from ..models.user import User
from ..models.job import Job
from ..models.video_delivery import VideoDelivery
from ..models.video_revision import VideoRevision
from ..schemas.video_revision import VideoRevisionCreate, VideoRevisionResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()

@router.post("", response_model=VideoRevisionResponse, status_code=status.HTTP_201_CREATED)
def request_revision(
    revision_in: VideoRevisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'brand':
        raise HTTPException(status_code=403, detail="Only brands can request revisions")
        
    delivery = db.query(VideoDelivery).filter(VideoDelivery.id == revision_in.delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
        
    job = db.query(Job).filter(Job.id == delivery.job_id).first()
    # TODO: Check brand ownership
    
    # Check max revisions
    allowed_revisions = job.max_revisions
    if job.addon_extra_revisions:
        allowed_revisions += 2 # Example: extra 2 revisions for addon
        
    if delivery.revision_count >= allowed_revisions:
        raise HTTPException(status_code=400, detail="Maximum revisions reached")

    revision = VideoRevision(
        **revision_in.model_dump()
    )
    db.add(revision)
    
    delivery.status = 'needs_revision'
    delivery.revision_count += 1
    
    db.commit()
    db.refresh(revision)
    return revision
