from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from ..database import get_db
from ..models.user import User
from ..models.creator_wallet import CreatorWallet
from ..models.wallet_transaction import WalletTransaction
from ..core.dependencies import get_current_active_user

router = APIRouter()

@router.get("")
def get_creator_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != "creator":
        raise HTTPException(status_code=403, detail="Only creators have creator wallets")
        
    wallet = db.query(CreatorWallet).filter(CreatorWallet.creator_id == current_user.id).first()
    if not wallet:
        wallet = CreatorWallet(creator_id=current_user.id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

@router.get("/transactions")
def get_wallet_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    wallet = db.query(CreatorWallet).filter(CreatorWallet.creator_id == current_user.id).first()
    if not wallet:
        return []
        
    transactions = db.query(WalletTransaction).filter(
        WalletTransaction.wallet_id == wallet.id,
        WalletTransaction.wallet_type == "creator"
    ).order_by(WalletTransaction.created_at.desc()).all()
    return transactions

@router.post("/payout")
def request_payout(
    amount: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # This would integrate with Stripe Connect
    wallet = db.query(CreatorWallet).filter(CreatorWallet.creator_id == current_user.id).first()
    if not wallet or wallet.available_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
        
    # Deduct and create transaction
    wallet.available_balance -= amount
    
    tx = WalletTransaction(
        wallet_id=wallet.id,
        wallet_type="creator",
        amount=amount,
        transaction_type="debit",
        description="Payout via Stripe Connect",
        status="pending"
    )
    db.add(tx)
    db.commit()
    
    return {"status": "payout_requested", "amount": amount}
