from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.creator import CreatorProfile
from ..schemas.creator import CreatorProfileCreate, CreatorProfileUpdate, CreatorProfileResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=CreatorProfileResponse)
def read_creator_profile_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'creator':
        raise HTTPException(status_code=403, detail="Not a creator")
        
    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.post("/me", response_model=CreatorProfileResponse, status_code=status.HTTP_201_CREATED)
def create_creator_profile_me(
    profile_in: CreatorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'creator':
        raise HTTPException(status_code=403, detail="Not a creator")
        
    existing = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists. Use PUT to update.")
        
    profile = CreatorProfile(user_id=current_user.id, **profile_in.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.put("/me", response_model=CreatorProfileResponse)
def update_creator_profile_me(
    profile_in: CreatorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
        
    db.commit()
    db.refresh(profile)
    return profile
