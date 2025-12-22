from sqlalchemy.orm import Session
from app.models.tag import Tag

def upsert_tags(db: Session, *, org_id: int, tag_names: list[str]) -> list[Tag]:
    tags: list[Tag] = []
    normalized = {t.strip().lower() for t in tag_names if t.strip()}
    for name in normalized:
        tag = db.query(Tag).filter(Tag.org_id == org_id, Tag.name == name).first()
        if not tag:
            tag = Tag(org_id=org_id, name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags
