from pydantic import BaseModel, Field
from typing import List, Optional


class DocumentUploadRequest(BaseModel):
    """Request model for document upload"""
    sessionId: str = Field(..., description="Session ID where the document belongs")

    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "550e8400-e29b-41d4-a716-446655440000"
            }
        }