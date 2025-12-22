from sqlalchemy.orm import Session
from app.models.activity import ActivityLog

def log_activity(db: Session, *, org_id: int, actor_user_id: int, action: str, entity: str, entity_id: int) -> None:
    db.add(ActivityLog(
        org_id=org_id,
        actor_user_id=actor_user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
    ))
