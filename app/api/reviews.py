from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..database import get_db
from ..models.user import User
from ..models.review import Review
from ..schemas.review import ReviewCreate, ReviewResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()

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
