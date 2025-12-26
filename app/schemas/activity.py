from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    entity: str
    entity_id: int
    actor_user_id: int
    created_at: datetime
