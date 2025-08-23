# api/v1/routes/auth.py
from fastapi import Depends, HTTPException, status, Request, APIRouter
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from datetime import timedelta
import os

from ..models.user import User
from api.db.database import get_db
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token
from api.core.google_auth import GoogleAuth
from api.core.security import get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, verify_password, get_current_user

router = APIRouter()

google_auth = GoogleAuth()

@router.post("/register", response_model=Token)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        auth_provider="email"
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await google_auth.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await google_auth.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
        
        user = db.query(User).filter(User.email == user_info['email']).first()
        
        if not user:
            user = User(
                email=user_info['email'],
                username=user_info.get('name', ''),
                google_id=user_info['sub'],
                auth_provider="google",
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            if not user.google_id:
                user.google_id = user_info['sub']
                user.auth_provider = "google"
                db.commit()

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        frontend_url = os.getenv("FRONTEND_URL")
        return RedirectResponse(url=f"{frontend_url}/auth/callback?access_token={access_token}")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_verified=current_user.is_verified,
        auth_provider=current_user.auth_provider,
        created_at=current_user.created_at
    )

@router.post("/logout")
async def logout_user():
    return {"message": "Successfully logged out"}