from pydantic import BaseModel
from typing import Optional


class DocumentId(BaseModel):
    documentId: str


class SessionId(BaseModel):
    sessionId: str


class UserId(BaseModel):
    userId: str


class BaseResponse(BaseModel):
    success: bool
    message: Optional[str] = None