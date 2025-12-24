from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import OrgRole
from app.schemas.auth import RegisterRequest, LoginRequest, TokenPair, RefreshRequest

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenPair)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    org_name = body.org_name.strip()
    if db.query(Organization).filter(Organization.name == org_name).first():
        raise HTTPException(status_code=409, detail="Organization name already exists")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    org = Organization(name=org_name)
    db.add(org)
    db.flush()

    user = User(
        org_id=org.id,
        email=body.email,
        hashed_password=hash_password(body.password),
        role=OrgRole.admin.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access = create_access_token(
        subject=user.email,
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        extra={"org_id": user.org_id, "role": user.role, "user_id": user.id},
    )
    refresh = create_refresh_token(
        subject=user.email,
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        expires_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    return {
        "access_token": access, 
        "refresh_token": refresh, 
        "token_type": "bearer",
        "role": user.role,
        "org_id": user.org_id,
        "user_id": user.id,
    }

@router.post("/login", response_model=TokenPair)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Swagger OAuth2 sends "username" + "password".
    # We treat username as email.
    email = form_data.username
    password = form_data.password
    
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(
        subject=user.email,
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        extra={"org_id": user.org_id, "role": user.role, "user_id": user.id},
    )
    refresh = create_refresh_token(
        subject=user.email,
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        expires_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    return {
        "access_token": access, 
        "refresh_token": refresh,
        "token_type": "bearer",
        "role": user.role,
        "org_id": user.org_id,
        "user_id": user.id,
    }

@router.post("/refresh", response_model=TokenPair)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(body.refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access = create_access_token(
        subject=user.email,
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        extra={"org_id": user.org_id, "role": user.role, "user_id": user.id},
    )
    refresh = create_refresh_token(
        subject=user.email,
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        expires_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    return {
        "access_token": access, 
        "refresh_token": refresh,
        "token_type": "bearer",
        "role": user.role,
        "org_id": user.org_id,
        "user_id": user.id,
    }
