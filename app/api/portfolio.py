from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..models.creator_portfolio import CreatorPortfolioItem
from ..core.dependencies import get_current_active_user

router = APIRouter()

class PortfolioItemCreate(BaseModel):
    title: str
    video_url: str
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None

@router.get("/{creator_id}")
def get_portfolio(
    creator_id: str,
    db: Session = Depends(get_db)
):
    items = db.query(CreatorPortfolioItem).filter(CreatorPortfolioItem.creator_id == creator_id).all()
    return items

@router.post("")
def add_portfolio_item(
    item_data: PortfolioItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != "creator":
        raise HTTPException(status_code=403, detail="Only creators can add portfolio items")
        
    item = CreatorPortfolioItem(
        creator_id=current_user.id,
        title=item_data.title,
        video_url=item_data.video_url,
        thumbnail_url=item_data.thumbnail_url,
        category=item_data.category
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}")
def delete_portfolio_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    item = db.query(CreatorPortfolioItem).filter(CreatorPortfolioItem.id == item_id).first()
    if not item or str(item.creator_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Item not found or unauthorized")
        
    db.delete(item)
    db.commit()
    return {"status": "success"}
