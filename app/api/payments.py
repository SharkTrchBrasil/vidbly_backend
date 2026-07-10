from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..database import get_db
from ..models.user import User
from ..models.payment import Payment
from ..schemas.payment import PaymentResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()

@router.get("", response_model=List[PaymentResponse])
def get_user_payments(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).offset(skip).limit(limit).all()
    return payments
