from pydantic import BaseModel, ConfigDict

class OrgOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
