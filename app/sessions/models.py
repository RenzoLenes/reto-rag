from pydantic import BaseModel, Field
from typing import Optional


class SessionCreate(BaseModel):
    name: str


class SessionUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="New session name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Mi sesión actualizada"
            }
        }


class SessionOut(BaseModel):
    sessionId: str
    name: str
    createdAt: str