from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..database import get_db
from ..models.user import User
from ..models.review import Review
from ..schemas.review import ReviewCreate, ReviewResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()

@router.get("", response_model=List[ReviewResponse])
def get_reviews(
    creator_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Review)
    if creator_id:
        query = query.filter(Review.reviewee_id == creator_id)
    return query.all()

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    review = Review(
        reviewer_id=current_user.id,
        **review_in.model_dump()
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    
    # TODO: Update creator/brand average rating
    return review
