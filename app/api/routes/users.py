from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role, get_current_user
from app.core.security import hash_password
from app.models.user import User
from app.models.enums import OrgRole
from app.schemas.user import UserCreate, UserOut
from app.services.activity_service import log_activity

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut, dependencies=[Depends(require_role(OrgRole.admin))])
def create_user(body: UserCreate, db: Session = Depends(get_db), actor=Depends(get_current_user)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        org_id=actor.org_id,
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_activity(db, org_id=actor.org_id, actor_user_id=actor.id, action="user.create", entity="user", entity_id=user.id)
    db.commit()
    return user

@router.get("", response_model=list[UserOut], dependencies=[Depends(require_role(OrgRole.admin))])
def list_users(db: Session = Depends(get_db), actor=Depends(get_current_user)):
    return db.query(User).filter(User.org_id == actor.org_id).order_by(User.id.asc()).all()
