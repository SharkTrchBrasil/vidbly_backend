from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import uuid

from ..database import get_db
from ..models.job import Job
from ..models.payment import Payment
from ..core.config import settings

router = APIRouter()

@router.post("/efi")
async def efi_webhook(request: Request, db: Session = Depends(get_db)):
    # Simple webhook for Efí PIX
    # TODO: Validate webhook signature using mTLS or EFI IPs
    data = await request.json()
    
    # Handle the 'pix' array in Efí payload
    if "pix" in data:
        for pix in data["pix"]:
            txid = pix.get("txid")
            if txid:
                job = db.query(Job).filter(Job.efi_txid == txid).first()
                if job and job.status == 'draft':
                    job.status = 'open'
                    
                    # Create payment record
                    from datetime import datetime, timezone
                    job.paid_at = datetime.now(timezone.utc)
                    
                    payment = Payment(
                        job_id=job.id,
                        user_id=job.brand_id, # Assuming brand_id is mapped correctly later
                        amount=job.total_price,
                        provider="efi",
                        provider_txid=txid,
                        status="completed",
                        payment_type="charge"
                    )
                    db.add(payment)
                    db.commit()
    
    return {"status": "received"}

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    # TODO: Validate Stripe Signature
    data = await request.json()
    return {"status": "received"}
