from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, timezone

from ..database import get_db
from ..models.user import User
from ..models.job import Job
from ..models.creator import CreatorProfile
from ..models.brand import BrandProfile
from ..models.video_delivery import VideoDelivery
from ..schemas.video_delivery import VideoDeliveryCreate, VideoDeliveryUpdate, VideoDeliveryResponse
from ..core.dependencies import get_current_active_user
from ..services.stripe_service import transfer_to_creator
from ..services.watermark_service import generate_watermark
from ..services.s3_storage import generate_presigned_view_url
from ..models.wallet_transaction import WalletTransaction
from ..models.creator_wallet import CreatorWallet
from ..models.wallet import BrandWallet
from ..models.payment import Payment

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

    # Generate watermark (synchronous for now)
    watermarked_key = None
    try:
        watermarked_key = generate_watermark(delivery_in.original_s3_key)
    except Exception as e:
        print(f"Watermark failed: {e}")
        # Continue without watermark or fail? The plan says to save both.
        raise HTTPException(status_code=500, detail="Failed to generate watermark")

    delivery = VideoDelivery(
        creator_id=creator_profile.id,
        job_id=delivery_in.job_id,
        original_s3_key=delivery_in.original_s3_key,
        watermarked_s3_key=watermarked_key,
        status="pending_review"
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return _populate_urls(delivery)

def _populate_urls(delivery: VideoDelivery) -> dict:
    del_dict = {
        "id": delivery.id,
        "job_id": delivery.job_id,
        "creator_id": delivery.creator_id,
        "status": delivery.status,
        "revision_count": delivery.revision_count,
        "submitted_at": delivery.submitted_at,
        "reviewed_at": delivery.reviewed_at,
        "watermarked_url": generate_presigned_view_url(delivery.watermarked_s3_key) if delivery.watermarked_s3_key else None,
        "original_url": generate_presigned_view_url(delivery.original_s3_key) if delivery.status == "approved" else None
    }
    return del_dict

@router.get("/job/{job_id}", response_model=List[VideoDeliveryResponse])
def get_job_deliveries(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    deliveries = db.query(VideoDelivery).filter(VideoDelivery.job_id == job_id).all()
    return [_populate_urls(d) for d in deliveries]

@router.get("/{delivery_id}/download")
def download_original(
    delivery_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    delivery = db.query(VideoDelivery).filter(VideoDelivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
        
    if delivery.status != 'approved':
        raise HTTPException(status_code=400, detail="Video must be approved before downloading original")
        
    job = db.query(Job).filter(Job.id == delivery.job_id).first()
    if current_user.user_type == 'brand':
        brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
        if job.brand_id != brand.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.user_type == 'creator':
        creator = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
        if delivery.creator_id != creator.id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
    url = generate_presigned_view_url(delivery.original_s3_key, expiration=86400) # 24 hours
    return {"download_url": url}

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
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    
    if job.brand_id != brand.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    delivery.status = 'approved'
    delivery.reviewed_at = datetime.now(timezone.utc)
    
    # Mark job as completed
    job.status = 'completed'
    
    # 1. Payment(charge) for Brand
    charge_record = Payment(
        job_id=job.id,
        user_id=current_user.id,
        amount=job.budget_per_video,
        provider="stripe",
        status="completed",
        payment_type="charge"
    )
    db.add(charge_record)
    db.flush()
    
    # 2. Stripe Payout to Creator
    creator = db.query(CreatorProfile).filter(CreatorProfile.id == delivery.creator_id).first()
    payout_amount = float(job.budget_per_video) * 0.8 # assuming 20% platform fee
    if creator and creator.stripe_account_id:
        try:
            transfer_id = transfer_to_creator(
                account_id=creator.stripe_account_id,
                amount=payout_amount
            )
            # Create payment record
            payout_record = Payment(
                job_id=job.id,
                user_id=creator.user_id,
                amount=payout_amount,
                provider="stripe",
                provider_txid=transfer_id,
                status="completed",
                payment_type="payout"
            )
            db.add(payout_record)
            db.flush()
            
            # Creator Wallet update
            creator_wallet = db.query(CreatorWallet).filter(CreatorWallet.creator_id == creator.id).first()
            if not creator_wallet:
                creator_wallet = CreatorWallet(creator_id=creator.id)
                db.add(creator_wallet)
                
            creator_wallet.available_balance += payout_amount
            creator_wallet.total_earned += payout_amount
            creator.total_earned = (creator.total_earned or 0.0) + float(payout_amount)
            
            # Creator Wallet Transaction
            tx = WalletTransaction(
                wallet_id=creator_wallet.id,
                wallet_type="creator",
                amount=payout_amount,
                transaction_type="credit",
                description=f"Pgto Job: {job.title}",
                job_id=job.id,
                payment_id=payout_record.id,
                category="job_payout",
                status="completed"
            )
            db.add(tx)
            
        except Exception as e:
            print(f"Failed to transfer to creator: {e}")
    
    db.commit()
    db.refresh(delivery)
    return _populate_urls(delivery)

@router.post("/{delivery_id}/refund")
def refund_delivery(
    delivery_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'admin' and current_user.user_type != 'brand': # Simplify auth for now
        raise HTTPException(status_code=403, detail="Not authorized to refund")
        
    delivery = db.query(VideoDelivery).filter(VideoDelivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
        
    job = db.query(Job).filter(Job.id == delivery.job_id).first()
    
    # 1. Reverse Balances
    brand_wallet = db.query(BrandWallet).filter(BrandWallet.brand_id == job.brand_id).first()
    if brand_wallet:
        brand_wallet.balance += float(job.budget_per_video)
        tx_brand = WalletTransaction(
            wallet_id=brand_wallet.id,
            wallet_type="brand",
            amount=float(job.budget_per_video),
            transaction_type="credit",
            description=f"Estorno Job: {job.title}",
            job_id=job.id,
            category="refund",
            status="completed"
        )
        db.add(tx_brand)
        
    creator = db.query(CreatorProfile).filter(CreatorProfile.id == delivery.creator_id).first()
    payout_amount = float(job.budget_per_video) * 0.8
    if creator:
        creator_wallet = db.query(CreatorWallet).filter(CreatorWallet.creator_id == creator.id).first()
        if creator_wallet:
            creator_wallet.available_balance -= payout_amount
            tx_creator = WalletTransaction(
                wallet_id=creator_wallet.id,
                wallet_type="creator",
                amount=payout_amount,
                transaction_type="debit",
                description=f"Estorno Job: {job.title}",
                job_id=job.id,
                category="refund",
                status="completed"
            )
            db.add(tx_creator)

    # Note: real stripe refund would be called here.
    
    # Update payment statuses
    payments = db.query(Payment).filter(Payment.job_id == job.id).all()
    for p in payments:
        p.status = "refunded"

    delivery.status = "refunded"
    job.status = "refunded"

    db.commit()
    return {"message": "Refund successful"}
