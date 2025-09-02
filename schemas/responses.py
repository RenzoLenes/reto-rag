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


class SessionDeleteResponse(BaseModel):
    """Response model for session deletion"""
    message: str = Field(..., description="Deletion success message")
    sessionId: str = Field(..., description="ID of the deleted session")
    documentsDeleted: int = Field(..., description="Number of documents deleted")
    embeddingsDeleted: int = Field(..., description="Number of embeddings deleted")
    messagesDeleted: int = Field(..., description="Number of messages deleted")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Session and all related data deleted successfully",
                "sessionId": "991cafc3-3948-4bf4-bb5f-acfd5652ebb8",
                "documentsDeleted": 3,
                "embeddingsDeleted": 25,
                "messagesDeleted": 12
            }
        }


class UserResponse(BaseModel):
    """Response model for user information"""
    userId: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")

    class Config:
        json_schema_extra = {
            "example": {
                "userId": "c2d7a715-dc12-4c73-b6df-7da5ec176204",
                "email": "usuario@ejemplo.com"
            }
        }


class DocumentInfo(BaseModel):
    """Document information model"""
    documentId: str = Field(..., description="Unique document identifier")
    fileName: str = Field(..., description="Original filename")
    pages: int = Field(..., description="Number of pages in document")
    uploadedAt: str = Field(..., description="Upload timestamp")
    s3Key: str = Field(..., description="S3 storage key")

    class Config:
        json_schema_extra = {
            "example": {
                "documentId": "e629dcc7-191f-4704-b1de-8975347311ce",
                "fileName": "UPC-RAG.pdf",
                "pages": 5,
                "uploadedAt": "2025-08-31T23:45:30.123Z",
                "s3Key": "users/user123/sessions/session456/documents/doc789/UPC-RAG.pdf"
            }
        }


class DocumentListResponse(BaseModel):
    """Response model for session documents list"""
    sessionId: str = Field(..., description="Session identifier")
    documents: List[DocumentInfo] = Field(..., description="List of documents in the session")
    totalDocuments: int = Field(..., description="Total number of documents")

    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "991cafc3-3948-4bf4-bb5f-acfd5652ebb8",
                "documents": [
                    {
                        "documentId": "e629dcc7-191f-4704-b1de-8975347311ce",
                        "fileName": "UPC-RAG.pdf",
                        "pages": 5,
                        "uploadedAt": "2025-08-31T23:45:30.123Z",
                        "s3Key": "users/user123/sessions/session456/documents/doc789/UPC-RAG.pdf"
                    }
                ],
                "totalDocuments": 1
            }
        }


class MessageInfo(BaseModel):
    """Message information model"""
    messageId: str = Field(..., description="Unique message identifier")
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    createdAt: str = Field(..., description="Message timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "messageId": "msg-550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "¿Cuál es el problema de investigación?",
                "createdAt": "2025-08-31T23:45:30.123Z"
            }
        }


class SessionMessagesResponse(BaseModel):
    """Response model for session messages list"""
    sessionId: str = Field(..., description="Session identifier")
    messages: List[MessageInfo] = Field(..., description="List of messages in the session")
    totalMessages: int = Field(..., description="Total number of messages")

    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "991cafc3-3948-4bf4-bb5f-acfd5652ebb8",
                "messages": [
                    {
                        "messageId": "msg-550e8400-e29b-41d4-a716-446655440000",
                        "role": "user",
                        "content": "¿Cuál es el problema de investigación?",
                        "createdAt": "2025-08-31T23:45:30.123Z"
                    },
                    {
                        "messageId": "msg-661f9511-f3ab-52e5-b827-557766551111",
                        "role": "assistant",
                        "content": "El problema de investigación es que los estudiantes de la UPC enfrentan dificultades...",
                        "createdAt": "2025-08-31T23:45:35.789Z"
                    }
                ],
                "totalMessages": 2
            }
        }