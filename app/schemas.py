from pydantic import BaseModel

class StatusResponse(BaseModel):
    damaged_system: str