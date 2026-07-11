from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional

from ..database import get_db
from ..models.wallet import BrandWallet
from ..models.brand import BrandProfile
from ..models.user import User
from ..models.wallet_transaction import WalletTransaction
from ..schemas.wallet import WalletResponse, WalletTransactionResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()

# Wallet plans pricing (BRL)
WALLET_PLANS = {
    "basic": {"price": 500, "bonus": 0},
    "essential": {"price": 1000, "bonus": 100},
    "professional": {"price": 2500, "bonus": 300},
    "refine": {"price": 5000, "bonus": 700},
}


@router.get("/", response_model=WalletResponse)
def get_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the brand's wallet balance."""
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    wallet = db.query(BrandWallet).filter(BrandWallet.brand_id == brand.id).first()
    if not wallet:
        # Auto-create wallet if it doesn't exist
        wallet = BrandWallet(brand_id=brand.id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    return wallet


@router.post("/topup/{plan_type}", response_model=WalletResponse)
def topup_wallet(
    plan_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Top up the brand's wallet with a plan. 
    In production, this would be called after payment confirmation via webhook."""
    if plan_type not in WALLET_PLANS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plan. Choose from: {list(WALLET_PLANS.keys())}"
        )
    
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    wallet = db.query(BrandWallet).filter(BrandWallet.brand_id == brand.id).first()
    if not wallet:
        wallet = BrandWallet(brand_id=brand.id)
        db.add(wallet)
        db.flush()
    
    plan = WALLET_PLANS[plan_type]
    wallet.balance += plan["price"]
    wallet.bonus_balance += plan["bonus"]
    wallet.plan_type = plan_type
    wallet.last_topup_at = datetime.now(timezone.utc)
    
    # Create WalletTransaction
    tx = WalletTransaction(
        wallet_id=wallet.id,
        wallet_type="brand",
        amount=plan["price"],
        transaction_type="credit",
        description=f"Recarga Plano {plan_type.capitalize()}",
        category="topup",
        status="completed"
    )
    db.add(tx)
    
    db.commit()
    db.refresh(wallet)
    return wallet


@router.post("/deduct/{amount}", response_model=WalletResponse)
def deduct_from_wallet(
    amount: float,
    job_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deduct from the brand's wallet when approving a creator for a job.
    Uses bonus balance first, then regular balance."""
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    wallet = db.query(BrandWallet).filter(BrandWallet.brand_id == brand.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found. Top up first.")
    
    total_available = wallet.balance + wallet.bonus_balance
    if amount > total_available:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Available: R$ {total_available:.2f}, Requested: R$ {amount:.2f}"
        )
    
    # Deduct from bonus first, then regular balance
    if amount <= wallet.bonus_balance:
        wallet.bonus_balance -= amount
    else:
        remaining = amount - wallet.bonus_balance
        wallet.bonus_balance = 0
        wallet.balance -= remaining
        
    tx = WalletTransaction(
        wallet_id=wallet.id,
        wallet_type="brand",
        amount=amount,
        transaction_type="debit",
        description="Contratação Job" if not job_id else f"Contratação Job (ID: {str(job_id)[:8]})",
        job_id=job_id,
        category="job_charge",
        status="completed"
    )
    db.add(tx)
    
    db.commit()
    db.refresh(wallet)
    return wallet


@router.get("/transactions", response_model=List[WalletTransactionResponse])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
        
    wallet = db.query(BrandWallet).filter(BrandWallet.brand_id == brand.id).first()
    if not wallet:
        return []
        
    transactions = db.query(WalletTransaction).filter(
        WalletTransaction.wallet_id == wallet.id,
        WalletTransaction.wallet_type == "brand"
    ).order_by(WalletTransaction.created_at.desc()).all()
    
    return transactions

