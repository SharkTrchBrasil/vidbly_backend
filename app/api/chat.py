from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models.chat import ChatMessage
from ..models.user import User
from ..schemas.chat import ChatMessageCreate, ChatMessageResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a chat message to another user within a job context."""
    msg = ChatMessage(
        job_id=payload.job_id,
        sender_id=current_user.id,
        receiver_id=payload.receiver_id,
        message=payload.message,
        message_type=payload.message_type
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@router.get("/job/{job_id}", response_model=List[ChatMessageResponse])
def get_messages_by_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all chat messages for a specific job (only if user is sender or receiver)."""
    messages = db.query(ChatMessage).filter(
        ChatMessage.job_id == job_id,
        (ChatMessage.sender_id == current_user.id) | (ChatMessage.receiver_id == current_user.id)
    ).order_by(ChatMessage.created_at.asc()).all()
    return messages


@router.put("/{message_id}/read", response_model=ChatMessageResponse)
def mark_as_read(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a message as read (only receiver can do this)."""
    msg = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.receiver_id == current_user.id
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    msg.is_read = True
    db.commit()
    db.refresh(msg)
    return msg


@router.get("/unread/count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get count of unread messages for the current user."""
    count = db.query(ChatMessage).filter(
        ChatMessage.receiver_id == current_user.id,
        ChatMessage.is_read == False
    ).count()
    return {"unread_count": count}
