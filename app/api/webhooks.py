from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import uuid

from ..database import get_db
from ..models.job import Job
from ..models.payment import Payment
from ..core.config import settings

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    # TODO: Validate Stripe Signature
    data = await request.json()
    return {"status": "received"}
