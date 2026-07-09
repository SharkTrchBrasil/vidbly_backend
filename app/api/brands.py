from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.brand import BrandProfile
from ..schemas.brand import BrandProfileCreate, BrandProfileUpdate, BrandProfileResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=BrandProfileResponse)
def read_brand_profile_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'brand':
        raise HTTPException(status_code=403, detail="Not a brand")
        
    profile = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.post("/me", response_model=BrandProfileResponse, status_code=status.HTTP_201_CREATED)
def create_brand_profile_me(
    profile_in: BrandProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'brand':
        raise HTTPException(status_code=403, detail="Not a brand")
        
    existing = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists. Use PUT to update.")
        
    profile = BrandProfile(user_id=current_user.id, **profile_in.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.put("/me", response_model=BrandProfileResponse)
def update_brand_profile_me(
    profile_in: BrandProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
        
    db.commit()
    db.refresh(profile)
    return profile
