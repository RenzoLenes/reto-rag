from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from sessions.routes import router as sessions_router
from documents.routes import router as documents_router
from chat.routes import router as chat_router
from core.config import settings
from schemas.responses import HealthCheckResponse, RootResponse

app = FastAPI(
    title="RAG Chatbot API",
    description="""
    ## Multimodal RAG Chatbot Backend
    
    This API provides a complete RAG (Retrieval-Augmented Generation) system for processing PDF documents 
    with both text and images, and providing intelligent chat responses based on document content.
    
    ### Features:
    - **User Authentication**: Register and login with JWT tokens
    - **Session Management**: Create and manage chat sessions
    - **Document Processing**: Upload and process PDF documents with text and image extraction
    - **Vector Search**: Find relevant content using semantic similarity
    - **Chat Interface**: Ask questions and get answers based on uploaded documents
    
    ### Getting Started:
    1. Register a new user account at `/auth/register`
    2. Login to get an access token at `/auth/login`
    3. Create a session at `/sessions/`
    4. Upload documents at `/documents/upload`
    5. Start chatting at `/chat/query`
    
    All endpoints (except auth) require authentication via Bearer token.
    """,
    version="1.0.0",
    contact={
        "name": "RAG Chatbot Support",
        "email": "support@ragchatbot.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS configuration for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(documents_router)
app.include_router(chat_router)


@app.get(
    "/health", 
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Check if the service is running properly",
    tags=["System"]
)
async def health_check():
    """
    Check the health status of the RAG Chatbot API.
    
    Returns:
        HealthCheckResponse: Service status information
    """
    return HealthCheckResponse(
        status="healthy",
        service="rag-chatbot",
        version="1.0.0"
    )


@app.get(
    "/", 
    response_model=RootResponse,
    summary="API Information",
    description="Get basic information about the API and available endpoints",
    tags=["System"]
)
async def root():
    """
    Get basic information about the RAG Chatbot API.
    
    Returns:
        RootResponse: API information and navigation links
    """
    return RootResponse(
        message="RAG Chatbot API",
        docs="/docs",
        health="/health"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.app_env == "dev"
    )