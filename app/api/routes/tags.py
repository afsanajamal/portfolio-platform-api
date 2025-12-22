from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role, get_current_user
from app.models.tag import Tag
from app.models.enums import OrgRole
from app.schemas.tag import TagCreate, TagOut
from app.services.activity_service import log_activity

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("", response_model=TagOut, dependencies=[Depends(require_role(OrgRole.admin, OrgRole.editor))])
def create_tag(body: TagCreate, db: Session = Depends(get_db), actor=Depends(get_current_user)):
    name = body.name.strip().lower()
    if db.query(Tag).filter(Tag.org_id == actor.org_id, Tag.name == name).first():
        raise HTTPException(status_code=409, detail="Tag already exists")

    tag = Tag(org_id=actor.org_id, name=name)
    db.add(tag)
    db.commit()
    db.refresh(tag)

    log_activity(db, org_id=actor.org_id, actor_user_id=actor.id, action="tag.create", entity="tag", entity_id=tag.id)
    db.commit()
    return tag

@router.get("", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db), actor=Depends(get_current_user)):
    return db.query(Tag).filter(Tag.org_id == actor.org_id).order_by(Tag.name.asc()).all()
