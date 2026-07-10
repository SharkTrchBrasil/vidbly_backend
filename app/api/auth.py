from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models.user import User
from ..schemas.auth import UserCreate, Token, UserResponse, GoogleLoginRequest
from ..core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from ..core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if user_in.user_type not in ['creator', 'brand']:
        raise HTTPException(status_code=400, detail="Invalid user_type")
        
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        user_type=user_in.user_type
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        subject=user.email, user_id=user.id, user_type=user.user_type, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        subject=user.email, user_id=user.id, user_type=user.user_type, expires_delta=refresh_token_expires
    )
    
    # Atualiza last_login
    from datetime import datetime, timezone
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/google", response_model=Token)
def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests
    import os
    
    # Ideally configure this via settings, but we will accept any valid Google token for now
    CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    
    try:
        # Verify token. If CLIENT_ID is empty, we just verify the signature and issuer
        if CLIENT_ID:
            idinfo = google_id_token.verify_oauth2_token(request.id_token, requests.Request(), CLIENT_ID)
        else:
            # Skip audience check if client ID not configured yet for testing
            idinfo = google_id_token.verify_oauth2_token(request.id_token, requests.Request())
            
        email = idinfo['email']
        name = idinfo.get('name', '')
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Registration flow
            if not request.user_type or request.user_type not in ['creator', 'brand']:
                raise HTTPException(status_code=400, detail="New users must specify user_type (creator or brand)")
                
            user = User(
                email=email,
                password_hash=get_password_hash(str(uuid.uuid4())), # Random password for OAuth users
                user_type=request.user_type,
                full_name=name,
                is_verified=True,
                email_verified_at=datetime.now(timezone.utc)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            subject=user.email, user_id=user.id, user_type=user.user_type, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            subject=user.email, user_id=user.id, user_type=user.user_type, expires_delta=refresh_token_expires
        )
        
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
