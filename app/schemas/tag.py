from pydantic import BaseModel, Field

class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class TagOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
