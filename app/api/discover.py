from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta

from ..database import get_db
from ..models.creator import CreatorProfile
from ..models.creator_service import CreatorService
from ..models.creator_tag import CreatorTag, creator_tag_association
from ..models.user import User
from ..schemas.creator import CreatorProfileResponse
from ..schemas.creator_service import CreatorServiceCreate, CreatorServiceUpdate, CreatorServiceResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()


# ═══════════════════════════════════════════════════════
# ADVANCED SEARCH (Billo-style filters)
# ═══════════════════════════════════════════════════════

@router.get("/search", response_model=List[CreatorProfileResponse])
def search_creators(
    # Basic filters
    search: Optional[str] = Query(None, description="Search by name"),
    gender: Optional[str] = Query(None, description="Male, Female, Other"),
    country_code: Optional[int] = Query(None, description="Country code (30=BR, 230=US)"),
    
    # Age filter (calculated from date_of_birth)
    age_min: Optional[int] = Query(None, description="Minimum age"),
    age_max: Optional[int] = Query(None, description="Maximum age"),
    
    # Creator tier
    premium_status: Optional[str] = Query(None, description="'approved' for Premium creators"),
    
    # Performance filters (sliders)
    ctr_min: Optional[float] = Query(None, description="Min CTR %"),
    ctr_max: Optional[float] = Query(None, description="Max CTR %"),
    hook_rate_min: Optional[float] = Query(None, description="Min Hook Rate %"),
    hook_rate_max: Optional[float] = Query(None, description="Max Hook Rate %"),
    roas_min: Optional[float] = Query(None, description="Min ROAS"),
    
    # Organic posting filters (sliders)
    organic_price_min: Optional[float] = Query(None, description="Min organic post price"),
    organic_price_max: Optional[float] = Query(None, description="Max organic post price"),
    cpv_min: Optional[float] = Query(None, description="Min cost per view"),
    cpv_max: Optional[float] = Query(None, description="Max cost per view"),
    views_min: Optional[int] = Query(None, description="Min views per reel"),
    views_max: Optional[int] = Query(None, description="Max views per reel"),
    followers_min: Optional[int] = Query(None, description="Min followers"),
    followers_max: Optional[int] = Query(None, description="Max followers"),
    
    # Partnership ads filter (slider)
    partnership_price_min: Optional[float] = Query(None, description="Min partnership ads price"),
    partnership_price_max: Optional[float] = Query(None, description="Max partnership ads price"),
    
    # Tag filters (comma-separated IDs)
    language_tags: Optional[str] = Query(None, description="Comma-separated tag IDs for Language"),
    interest_tags: Optional[str] = Query(None, description="Comma-separated tag IDs for Interests"),
    occupation_tags: Optional[str] = Query(None, description="Comma-separated tag IDs for Occupation"),
    ethnicity_tags: Optional[str] = Query(None, description="Comma-separated tag IDs for Ethnicity"),
    lifestyle_tags: Optional[str] = Query(None, description="Comma-separated tag IDs for Lifestyle"),
    appearance_tags: Optional[str] = Query(None, description="Comma-separated tag IDs for Appearance"),
    
    # Service filters
    service_platform: Optional[str] = Query(None, description="instagram, tiktok, meta"),
    service_type: Optional[str] = Query(None, description="organic_post, partnership_ads, spark_ads"),
    
    # Pagination
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    
    # Sort
    sort_by: Optional[str] = Query("rating", description="rating, completed_jobs, performance_ctr"),
    
    db: Session = Depends(get_db)
):
    """Advanced creator search with all Billo-style filters."""
    
    query = db.query(CreatorProfile).filter(CreatorProfile.is_approved == True)
    
    # Name search
    if search:
        query = query.filter(
            or_(
                CreatorProfile.first_name.ilike(f"%{search}%"),
                CreatorProfile.last_name.ilike(f"%{search}%")
            )
        )
    
    # Basic filters
    if gender:
        query = query.filter(CreatorProfile.gender == gender)
    if country_code:
        query = query.filter(CreatorProfile.country_code == country_code)
    if premium_status:
        query = query.filter(CreatorProfile.premium_status == premium_status)
    
    # Age filter
    if age_min or age_max:
        now = datetime.now(timezone.utc)
        if age_max:
            min_dob = now - timedelta(days=age_max * 365)
            query = query.filter(CreatorProfile.date_of_birth >= min_dob)
        if age_min:
            max_dob = now - timedelta(days=age_min * 365)
            query = query.filter(CreatorProfile.date_of_birth <= max_dob)
    
    # Performance range filters
    if ctr_min is not None:
        query = query.filter(CreatorProfile.performance_ctr >= ctr_min)
    if ctr_max is not None:
        query = query.filter(CreatorProfile.performance_ctr <= ctr_max)
    if hook_rate_min is not None:
        query = query.filter(CreatorProfile.performance_hook_rate >= hook_rate_min)
    if hook_rate_max is not None:
        query = query.filter(CreatorProfile.performance_hook_rate <= hook_rate_max)
    if roas_min is not None:
        query = query.filter(CreatorProfile.performance_roas >= roas_min)
    
    # Organic posting filters
    if organic_price_min is not None:
        query = query.filter(CreatorProfile.organic_post_price >= organic_price_min)
    if organic_price_max is not None:
        query = query.filter(CreatorProfile.organic_post_price <= organic_price_max)
    if cpv_min is not None:
        query = query.filter(CreatorProfile.cost_per_view >= cpv_min)
    if cpv_max is not None:
        query = query.filter(CreatorProfile.cost_per_view <= cpv_max)
    if views_min is not None:
        query = query.filter(CreatorProfile.views_per_reel >= views_min)
    if views_max is not None:
        query = query.filter(CreatorProfile.views_per_reel <= views_max)
    if followers_min is not None:
        query = query.filter(CreatorProfile.followers_count >= followers_min)
    if followers_max is not None:
        query = query.filter(CreatorProfile.followers_count <= followers_max)
    
    # Partnership ads filter
    if partnership_price_min is not None:
        query = query.filter(CreatorProfile.partnership_ads_price >= partnership_price_min)
    if partnership_price_max is not None:
        query = query.filter(CreatorProfile.partnership_ads_price <= partnership_price_max)
    
    # Tag-based filters (join with association table)
    all_tag_ids = []
    for tag_param in [language_tags, interest_tags, occupation_tags, ethnicity_tags, lifestyle_tags, appearance_tags]:
        if tag_param:
            ids = [int(x.strip()) for x in tag_param.split(",") if x.strip()]
            all_tag_ids.extend(ids)
    
    if all_tag_ids:
        query = query.join(creator_tag_association).filter(
            creator_tag_association.c.tag_id.in_(all_tag_ids)
        )
    
    # Service-based filter
    if service_platform or service_type:
        service_query = query.join(CreatorService, CreatorService.creator_id == CreatorProfile.id)
        service_query = service_query.filter(CreatorService.is_active == True)
        if service_platform:
            service_query = service_query.filter(CreatorService.platform == service_platform)
        if service_type:
            service_query = service_query.filter(CreatorService.service_type == service_type)
        query = service_query
    
    # Sorting
    sort_map = {
        "rating": CreatorProfile.rating.desc(),
        "completed_jobs": CreatorProfile.completed_jobs.desc(),
        "performance_ctr": CreatorProfile.performance_ctr.desc().nullslast(),
        "performance_roas": CreatorProfile.performance_roas.desc().nullslast(),
        "newest": CreatorProfile.created_at.desc(),
    }
    order = sort_map.get(sort_by, CreatorProfile.rating.desc())
    query = query.order_by(order)
    
    # Pagination
    creators = query.offset(skip).limit(limit).all()
    return creators


# ═══════════════════════════════════════════════════════
# CREATOR SERVICES (pricing per service)
# ═══════════════════════════════════════════════════════

@router.post("/me/services", response_model=CreatorServiceResponse, status_code=status.HTTP_201_CREATED)
def add_service(
    payload: CreatorServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a service offering with pricing (e.g. Instagram Reel at R$50)."""
    creator = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    
    # Check for duplicate
    existing = db.query(CreatorService).filter(
        CreatorService.creator_id == creator.id,
        CreatorService.service_type == payload.service_type,
        CreatorService.platform == payload.platform,
        CreatorService.subtype == payload.subtype
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Service already exists. Use PUT to update price.")
    
    service = CreatorService(
        creator_id=creator.id,
        service_type=payload.service_type,
        platform=payload.platform,
        subtype=payload.subtype,
        price=payload.price,
        is_active=payload.is_active
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/me/services", response_model=List[CreatorServiceResponse])
def list_my_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all services offered by the current creator."""
    creator = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    return db.query(CreatorService).filter(CreatorService.creator_id == creator.id).all()


@router.put("/me/services/{service_id}", response_model=CreatorServiceResponse)
def update_service(
    service_id: UUID,
    payload: CreatorServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update price or toggle active status on a service."""
    creator = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    
    service = db.query(CreatorService).filter(
        CreatorService.id == service_id,
        CreatorService.creator_id == creator.id
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(service, key, value)
    
    db.commit()
    db.refresh(service)
    return service


@router.get("/{creator_id}/services", response_model=List[CreatorServiceResponse])
def list_creator_services(
    creator_id: UUID,
    db: Session = Depends(get_db)
):
    """List services offered by a specific creator (public, for brands browsing)."""
    return db.query(CreatorService).filter(
        CreatorService.creator_id == creator_id,
        CreatorService.is_active == True
    ).all()


@router.get("/services/available")
def list_available_services():
    """List all platform service types available for creators to offer."""
    from ..models.creator_service import PLATFORM_SERVICES
    return PLATFORM_SERVICES
