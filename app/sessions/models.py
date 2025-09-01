from pydantic import BaseModel
from typing import Optional


class SessionCreate(BaseModel):
    name: str


class SessionOut(BaseModel):
    sessionId: str
    name: str
    createdAt: str