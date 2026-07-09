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

from ..services import stripe_service
from pydantic import BaseModel

class StripeOnboardingResponse(BaseModel):
    url: str

@router.post("/me/stripe/onboarding", response_model=StripeOnboardingResponse)
def create_stripe_onboarding(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Complete profile first.")

    # Se ainda não tem conta Stripe, cria
    if not profile.stripe_account_id:
        try:
            account_id = stripe_service.create_connect_account(
                email=current_user.email,
                first_name=profile.first_name,
                last_name=profile.last_name,
                cpf=profile.cpf or "00000000000" # fallback temporário
            )
            profile.stripe_account_id = account_id
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao criar conta na Stripe: {str(e)}")

    # Gera o link
    # TODO: Configurar as URLs reais de retorno para o seu app/site (Deep link)
    return_url = "https://vidbly.com/stripe/success" 
    refresh_url = "https://vidbly.com/stripe/refresh"

    try:
        url = stripe_service.generate_onboarding_link(
            account_id=profile.stripe_account_id,
            return_url=return_url,
            refresh_url=refresh_url
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar link da Stripe: {str(e)}")

@router.get("/me/stripe/status")
def check_stripe_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not profile or not profile.stripe_account_id:
        raise HTTPException(status_code=400, detail="Sem conta na Stripe vinculada.")

    is_complete = stripe_service.check_onboarding_status(profile.stripe_account_id)
    
    if is_complete and not profile.stripe_onboarding_complete:
        profile.stripe_onboarding_complete = True
        db.commit()
        
    return {"stripe_onboarding_complete": is_complete}
