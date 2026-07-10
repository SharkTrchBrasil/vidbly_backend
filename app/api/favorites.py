from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from ..database import get_db
from ..models.user import User
from ..models.favorite import Favorite
from ..core.dependencies import get_current_active_user

router = APIRouter()

@router.get("")
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != "brand":
        raise HTTPException(status_code=403, detail="Only brands can have favorites")
        
    favorites = db.query(Favorite).filter(Favorite.brand_id == current_user.id).all()
    return favorites

@router.post("/{creator_id}")
def add_favorite(
    creator_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != "brand":
        raise HTTPException(status_code=403, detail="Only brands can have favorites")
        
    existing = db.query(Favorite).filter(
        Favorite.brand_id == current_user.id,
        Favorite.creator_id == creator_id
    ).first()
    
    if existing:
        return existing
        
    fav = Favorite(brand_id=current_user.id, creator_id=creator_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav

@router.delete("/{creator_id}")
def remove_favorite(
    creator_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    fav = db.query(Favorite).filter(
        Favorite.brand_id == current_user.id,
        Favorite.creator_id == creator_id
    ).first()
    
    if fav:
        db.delete(fav)
        db.commit()
    return {"status": "success"}
