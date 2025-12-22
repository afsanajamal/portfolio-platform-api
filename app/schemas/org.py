from pydantic import BaseModel

class OrgOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
