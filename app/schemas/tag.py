from pydantic import BaseModel, Field, ConfigDict

class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
