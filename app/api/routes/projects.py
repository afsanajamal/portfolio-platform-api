from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.deps import get_db, require_role, get_current_user
from app.models.project import Project
from app.models.tag import Tag
from app.models.enums import OrgRole
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.tag_service import upsert_tags
from app.services.activity_service import log_activity

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectOut, dependencies=[Depends(require_role(OrgRole.admin, OrgRole.editor))])
def create_project(body: ProjectCreate, db: Session = Depends(get_db), actor=Depends(get_current_user)):
    project = Project(
        org_id=actor.org_id,
        owner_id=actor.id,
        title=body.title.strip(),
        description=body.description.strip(),
        github_url=body.github_url,
        is_public=body.is_public,
    )
    project.tags = upsert_tags(db, org_id=actor.org_id, tag_names=body.tag_names)
    db.add(project)
    db.commit()
    db.refresh(project)

    log_activity(db, org_id=actor.org_id, actor_user_id=actor.id, action="project.create", entity="project", entity_id=project.id)
    db.commit()

    return project

@router.get("", response_model=list[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    actor=Depends(get_current_user),
    q: str | None = None,
    tag: str | None = None,
    public_only: bool = False,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    sort: str = Query("newest", pattern="^(newest|oldest|title_asc|title_desc)$"),
):
    query = db.query(Project).filter(Project.org_id == actor.org_id)

    if public_only:
        query = query.filter(Project.is_public.is_(True))

    if q:
        query = query.filter(or_(Project.title.ilike(f"%{q}%"), Project.description.ilike(f"%{q}%")))

    if tag:
        tag_norm = tag.strip().lower()
        query = query.join(Project.tags).filter(Tag.org_id == actor.org_id, Tag.name == tag_norm)

    if sort == "newest":
        query = query.order_by(Project.id.desc())
    elif sort == "oldest":
        query = query.order_by(Project.id.asc())
    elif sort == "title_asc":
        query = query.order_by(Project.title.asc())
    else:
        query = query.order_by(Project.title.desc())

    projects = query.offset(offset).limit(limit).all()
    return projects

@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, body: ProjectUpdate, db: Session = Depends(get_db), actor=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.org_id == actor.org_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")

    if actor.role == OrgRole.viewer.value:
        raise HTTPException(status_code=403, detail="Insufficient role")

    if body.title is not None:
        project.title = body.title.strip()
    if body.description is not None:
        project.description = body.description.strip()
    if body.github_url is not None:
        project.github_url = body.github_url
    if body.is_public is not None:
        project.is_public = body.is_public
    if body.tag_names is not None:
        project.tags = upsert_tags(db, org_id=actor.org_id, tag_names=body.tag_names)

    db.commit()
    db.refresh(project)

    log_activity(db, org_id=actor.org_id, actor_user_id=actor.id, action="project.update", entity="project", entity_id=project.id)
    db.commit()

    return project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), actor=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.org_id == actor.org_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")

    if actor.role != OrgRole.admin.value and project.owner_id != actor.id:
        raise HTTPException(status_code=403, detail="Insufficient role")

    db.delete(project)
    db.commit()

    log_activity(db, org_id=actor.org_id, actor_user_id=actor.id, action="project.delete", entity="project", entity_id=project_id)
    db.commit()

    return {"ok": True}
