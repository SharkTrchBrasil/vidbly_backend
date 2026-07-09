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
        
    # Calculate platform fee (25%)
    platform_fee = job_in.budget_per_video * 0.25
    total_price = job_in.budget_per_video + platform_fee
    
    job = Job(
        brand_id=brand_profile.id,
        platform_fee=platform_fee,
        total_price=total_price,
        **job_in.model_dump()
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
    if 'budget_per_video' in update_data:
        # Recalculate fees
        job.platform_fee = update_data['budget_per_video'] * 0.25
        job.total_price = update_data['budget_per_video'] + job.platform_fee
        
    for field, value in update_data.items():
        setattr(job, field, value)
        
    db.commit()
    db.refresh(job)
    return job
