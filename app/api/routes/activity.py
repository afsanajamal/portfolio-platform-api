from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role, get_current_user
from app.models.activity import ActivityLog
from app.models.enums import OrgRole
from app.schemas.activity import ActivityOut

router = APIRouter(prefix="/activity", tags=["activity"])

@router.get("", response_model=list[ActivityOut], dependencies=[Depends(require_role(OrgRole.admin))])
def list_activity(
    db: Session = Depends(get_db),
    actor=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.org_id == actor.org_id)
        .order_by(ActivityLog.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
