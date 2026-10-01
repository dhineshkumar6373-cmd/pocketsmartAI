from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.db import User
from app.models.schemas import LoginRequest, RegisterRequest
from app.security import COOKIE_NAME, create_access_token, hash_password, verify_password

router = APIRouter()

@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(or_(User.username == payload.username, User.email == str(payload.email))))
    if existing:
        raise HTTPException(status_code=409, detail="Username or email already registered")
    user = User(username=payload.username, email=str(payload.email), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    return {"message": "Account created", "username": user.username}

@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(user.id, user.username)
    response.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", secure=not settings.debug, max_age=settings.session_max_age_minutes * 60)
    return {"message": "Logged in", "username": user.username}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"message": "Logged out"}

@router.get("/session-info")
def session_info(user: User = Depends(get_current_user)):
    return {"authenticated": True, "user_id": user.id, "username": user.username, "email": user.email}

@router.get("/session-data")
def session_data(user: User = Depends(get_current_user)):
    return {"username": user.username, "created_at": user.created_at.isoformat(), "history_count": len(user.history)}

@router.post("/token")
def token(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """JWT token endpoint kept for compatibility with the project specification."""
    return login(payload, response, db)
