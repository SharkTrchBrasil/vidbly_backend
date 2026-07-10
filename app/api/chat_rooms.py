from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, timezone

from ..database import get_db
from ..models.user import User
from ..models.chat_room import ChatRoom
from ..models.job import Job
from ..core.dependencies import get_current_active_user

router = APIRouter()

@router.get("")
def get_user_chat_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type == "brand":
        rooms = db.query(ChatRoom).filter(ChatRoom.brand_user_id == current_user.id).all()
    else:
        rooms = db.query(ChatRoom).filter(ChatRoom.creator_user_id == current_user.id).all()
    return rooms

@router.post("")
def create_chat_room(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing_room = db.query(ChatRoom).filter(ChatRoom.job_id == job_id).first()
    if existing_room:
        return existing_room

    # Note: Using the job creator (brand) and the accepted candidate.
    # If job doesn't have an accepted candidate yet, the room should not be created.
    # Assuming for this mock we just use placeholder values if missing.
    
    room = ChatRoom(
        job_id=job.id,
        brand_user_id=job.brand_id,
        creator_user_id=current_user.id if current_user.user_type == "creator" else job.brand_id, # Should be the assigned creator in reality
        last_message_at=datetime.now(timezone.utc)
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room
