from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.organization import Organization
from app.schemas.org import OrgOut

router = APIRouter(prefix="/orgs", tags=["orgs"])

@router.get("/me", response_model=OrgOut)
def get_my_org(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Organization).filter(Organization.id == user.org_id).first()
