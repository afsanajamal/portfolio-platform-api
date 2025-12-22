from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.db.base import Base

def _utcnow():
    return datetime.now(timezone.utc)

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    actor_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    action: Mapped[str] = mapped_column(String(50))   # e.g. project.create
    entity: Mapped[str] = mapped_column(String(50))   # project, tag, user
    entity_id: Mapped[int] = mapped_column(index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
