from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..database import get_db
from ..models.user import User
from ..models.brand import BrandProfile
from ..models.job import Job
from ..schemas.job import JobCreate, JobUpdate, JobResponse
from ..core.dependencies import get_current_active_user

def calculate_job_pricing(job_data: dict) -> tuple[float, float, float]:
    """Returns (budget_per_video, platform_fee, total_price) based on tier and addons"""
    base_prices = {
        "depoimento": 89.0,
        "unboxing": 149.0,
        "review": 249.0,
        "premium": 399.0,
        "pack": 349.0
    }
    
    tier = job_data.get("pricing_tier", "depoimento")
    base_price = base_prices.get(tier, 89.0)
    
    # Add-ons
    addons = 0.0
    if job_data.get("addon_express_delivery"): addons += 49.0
    if job_data.get("addon_pro_editing"): addons += 79.0
    if job_data.get("addon_premium_creator"): addons += 39.0
    if job_data.get("addon_extra_revisions"): addons += 29.0
    if job_data.get("addon_extended_rights"): addons += 59.0
    
    total_price = base_price + addons
    platform_fee = total_price * 0.25
    budget_per_video = total_price - platform_fee
    
    return budget_per_video, platform_fee, total_price


router = APIRouter()

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'brand':
        raise HTTPException(status_code=403, detail="Only brands can create jobs")
        
    brand_profile = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not brand_profile:
        raise HTTPException(status_code=400, detail="Brand profile not setup")
        
    # Calculate pricing dynamically
    job_dict = job_in.model_dump()
    budget, fee, total = calculate_job_pricing(job_dict)
    
    job_dict["budget_per_video"] = budget
    job_dict["platform_fee"] = fee
    job_dict["total_price"] = total
    
    job = Job(
        brand_id=brand_profile.id,
        **job_dict
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("", response_model=List[JobResponse])
def get_jobs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # If creator, only show 'open' jobs
    # If brand, show their own jobs
    if current_user.user_type == 'creator':
        jobs = db.query(Job).filter(Job.status == 'open').offset(skip).limit(limit).all()
    else:
        brand_profile = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
        if not brand_profile:
            return []
        jobs = db.query(Job).filter(Job.brand_id == brand_profile.id).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if current_user.user_type == 'brand':
        brand_profile = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
        if job.brand_id != brand_profile.id:
            raise HTTPException(status_code=403, detail="Not your job")
            
    return job

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: uuid.UUID,
    job_in: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'brand':
        raise HTTPException(status_code=403, detail="Not a brand")
        
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    brand_profile = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if job.brand_id != brand_profile.id:
        raise HTTPException(status_code=403, detail="Not your job")
        
    if job.status != 'draft':
        raise HTTPException(status_code=400, detail="Cannot edit a job that is not a draft")
        
    update_data = job_in.model_dump(exclude_unset=True)
    
    # If pricing tier or any addon is updated, recalculate pricing
    pricing_fields = ["pricing_tier", "addon_express_delivery", "addon_pro_editing", 
                      "addon_premium_creator", "addon_extra_revisions", "addon_extended_rights"]
    
    if any(field in update_data for field in pricing_fields):
        # Merge current job data with updates to calculate new price
        current_data = {
            "pricing_tier": job.pricing_tier,
            "addon_express_delivery": job.addon_express_delivery,
            "addon_pro_editing": job.addon_pro_editing,
            "addon_premium_creator": job.addon_premium_creator,
            "addon_extra_revisions": job.addon_extra_revisions,
            "addon_extended_rights": job.addon_extended_rights,
        }
        current_data.update(update_data)
        
        budget, fee, total = calculate_job_pricing(current_data)
        job.budget_per_video = budget
        job.platform_fee = fee
        job.total_price = total
        
    for field, value in update_data.items():
        setattr(job, field, value)
        
    db.commit()
    db.refresh(job)
    return job
