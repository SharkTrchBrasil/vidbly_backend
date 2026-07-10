from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, timezone

from ..database import get_db
from ..models.user import User
from ..models.job import Job
from ..models.creator import CreatorProfile
from ..models.video_delivery import VideoDelivery
from ..schemas.video_delivery import VideoDeliveryCreate, VideoDeliveryUpdate, VideoDeliveryResponse
from ..core.dependencies import get_current_active_user
from ..services.stripe_service import transfer_to_creator

router = APIRouter()

@router.post("", response_model=VideoDeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(
    delivery_in: VideoDeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'creator':
        raise HTTPException(status_code=403, detail="Only creators can submit deliveries")
        
    creator_profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not creator_profile:
        raise HTTPException(status_code=400, detail="Creator profile not setup")
        
    job = db.query(Job).filter(Job.id == delivery_in.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job.status != 'in_progress':
        raise HTTPException(status_code=400, detail="Job is not in progress")

    delivery = VideoDelivery(
        creator_id=creator_profile.id,
        **delivery_in.model_dump()
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery

@router.put("/{delivery_id}/approve", response_model=VideoDeliveryResponse)
def approve_delivery(
    delivery_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'brand':
        raise HTTPException(status_code=403, detail="Only brands can approve deliveries")
        
    delivery = db.query(VideoDelivery).filter(VideoDelivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
        
    job = db.query(Job).filter(Job.id == delivery.job_id).first()
    # TODO: Check brand ownership
    
    delivery.status = 'approved'
    delivery.reviewed_at = datetime.now(timezone.utc)
    
    # Mark job as completed
    job.status = 'completed'
    
    # Trigger Stripe Payout to Creator
    creator = db.query(CreatorProfile).filter(CreatorProfile.id == delivery.creator_id).first()
    if creator and creator.stripe_account_id:
        try:
            transfer_id = transfer_to_creator(
                account_id=creator.stripe_account_id,
                amount=job.budget_per_video
            )
            # Create payment record
            from ..models.payment import Payment
            payout_record = Payment(
                job_id=job.id,
                user_id=creator.user_id,
                amount=job.budget_per_video,
                provider="stripe",
                provider_txid=transfer_id,
                status="completed",
                payment_type="payout"
            )
            db.add(payout_record)
        except Exception as e:
            print(f"Failed to transfer to creator: {e}")
            # Consider alerting admin or flagging the delivery
    
    db.commit()
    db.refresh(delivery)
    return delivery
