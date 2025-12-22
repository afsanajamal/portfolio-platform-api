from fastapi import APIRouter
from app.api.routes import auth, orgs, users, projects, tags, activity

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(orgs.router)
api_router.include_router(users.router)
api_router.include_router(tags.router)
api_router.include_router(projects.router)
api_router.include_router(activity.router)
