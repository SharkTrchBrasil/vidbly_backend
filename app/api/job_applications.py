from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..database import get_db
from ..models.user import User
from ..models.job import Job
from ..models.creator import CreatorProfile
from ..models.job_application import JobApplication
from ..schemas.job_application import JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()

@router.post("", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    application_in: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'creator':
        raise HTTPException(status_code=403, detail="Only creators can apply to jobs")
        
    creator_profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not creator_profile:
        raise HTTPException(status_code=400, detail="Creator profile not setup")
        
    job = db.query(Job).filter(Job.id == application_in.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job.status != 'open':
        raise HTTPException(status_code=400, detail="Job is not open for applications")

    # Check if already applied
    existing = db.query(JobApplication).filter(
        JobApplication.job_id == job.id, 
        JobApplication.creator_id == creator_profile.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")
        
    application = JobApplication(
        creator_id=creator_profile.id,
        **application_in.model_dump()
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

@router.get("/job/{job_id}", response_model=List[JobApplicationResponse])
def get_job_applications(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Both brand (owner) and creator (applicant) can view, but filtered
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if current_user.user_type == 'brand':
        # Brand can see all apps for their job
        # TODO: Check brand ownership
        applications = db.query(JobApplication).filter(JobApplication.job_id == job_id).all()
        return applications
    elif current_user.user_type == 'creator':
        # Creator can only see their own app
        creator_profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
        applications = db.query(JobApplication).filter(
            JobApplication.job_id == job_id,
            JobApplication.creator_id == creator_profile.id
        ).all()
        return applications
    
    return []

@router.put("/{app_id}/status", response_model=JobApplicationResponse)
def update_application_status(
    app_id: uuid.UUID,
    status_update: JobApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != 'brand':
        raise HTTPException(status_code=403, detail="Only brands can accept/reject applications")
        
    application = db.query(JobApplication).filter(JobApplication.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    job = db.query(Job).filter(Job.id == application.job_id).first()
    # TODO: Check if brand owns this job
    
    new_status = status_update.status
    if new_status not in ['accepted', 'rejected']:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    application.status = new_status
    
    if new_status == 'accepted':
        # Also update job status if needed
        job.status = 'in_progress'
        job.accepted_creators += 1
        
    db.commit()
    db.refresh(application)
    return application
