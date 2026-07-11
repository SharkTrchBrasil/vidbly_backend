from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import uuid

from ..database import get_db
from ..models.job import Job
from ..models.payment import Payment
from ..models.creator import CreatorProfile
from ..core.config import settings
import stripe
from datetime import datetime, timezone

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        job_id = session.get('metadata', {}).get('job_id')
        if job_id:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                # Based on the requested flow, job could go to 'open' or just record the payment
                job.paid_at = datetime.now(timezone.utc)
                job.status = 'open' # Usually paid means the job is now open to creators
                db.commit()
    elif event['type'] == 'account.updated':
        account = event['data']['object']
        account_id = account.get('id')
        
        creator = db.query(CreatorProfile).filter(CreatorProfile.stripe_account_id == account_id).first()
        if creator:
            if len(account.get('requirements', {}).get('currently_due', [])) == 0:
                creator.stripe_onboarding_complete = True
            else:
                creator.stripe_onboarding_complete = False
            db.commit()

    return {"status": "success"}
