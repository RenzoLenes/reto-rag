from pydantic import BaseModel, Field
from typing import List, Optional


class DocumentUploadResponse(BaseModel):
    """Response model for document upload endpoint"""
    documentId: str = Field(..., description="Unique identifier for the uploaded document")
    fileName: str = Field(..., description="Name of the uploaded file")
    s3Key: str = Field(..., description="S3 key where the file is stored")
    pages: int = Field(..., description="Number of pages in the document")
    chunksIndexed: int = Field(..., description="Number of chunks indexed for search")

    class Config:
        json_schema_extra = {
            "example": {
                "documentId": "550e8400-e29b-41d4-a716-446655440000",
                "fileName": "sample_document.pdf",
                "s3Key": "users/user123/sessions/session456/documents/doc789/sample_document.pdf",
                "pages": 10,
                "chunksIndexed": 25
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "rag-chatbot",
                "version": "1.0.0"
            }
        }


class RootResponse(BaseModel):
    """Response model for root endpoint"""
    message: str = Field(..., description="Welcome message")
    docs: str = Field(..., description="Documentation URL")
    health: str = Field(..., description="Health check URL")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "RAG Chatbot API",
                "docs": "/docs",
                "health": "/health"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str = Field(..., description="Error message description")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Resource not found"
            }
        }