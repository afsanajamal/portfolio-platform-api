from pydantic import BaseModel, Field, ConfigDict
from app.schemas.tag import TagOut

class ProjectCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=1)
    github_url: str | None = Field(default=None, max_length=500)
    is_public: bool = False
    tag_names: list[str] = []

class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    github_url: str | None = Field(default=None, max_length=500)
    is_public: bool | None = None
    tag_names: list[str] | None = None

class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    owner_id: int
    title: str
    description: str
    github_url: str | None
    is_public: bool
    tags: list[TagOut]
