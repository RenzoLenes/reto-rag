from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from core.security import get_current_user
from core.utils import generate_uuid, get_current_timestamp, sanitize_text_for_json
from db.astra_client import astra_client
from chat.retriever import rag_retriever
from chat.rag_chain import rag_chain
from schemas.responses import ErrorResponse

router = APIRouter(
    prefix="/chat", 
    tags=["Chat"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing token"},
        404: {"model": ErrorResponse, "description": "Session not found or doesn't belong to user"},
        500: {"model": ErrorResponse, "description": "Error processing chat query"}
    }
)


class ChatQuery(BaseModel):
    """Request model for chat queries"""
    sessionId: str = Field(..., description="Session ID for the chat conversation")
    message: str = Field(..., min_length=1, max_length=2000, description="User message/question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "550e8400-e29b-41d4-a716-446655440000",
                "message": "What are the main topics discussed in the uploaded document?"
            }
        }


class SourceInfo(BaseModel):
    """Information about document sources used in the response"""
    documentId: str = Field(..., description="Unique identifier of the source document")
    fileName: str = Field(..., description="Name of the source document")
    page: int = Field(..., description="Page number in the document")
    source: str = Field(..., description="Type of source (text, image, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "documentId": "550e8400-e29b-41d4-a716-446655440000",
                "fileName": "sample_document.pdf",
                "page": 5,
                "source": "text"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat queries"""
    answer: str = Field(..., description="AI-generated response based on document content")
    sources: List[SourceInfo] = Field(..., description="List of document sources used to generate the answer")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Based on the uploaded documents, the main topics include artificial intelligence, machine learning algorithms, and data processing techniques. The documents provide detailed explanations of neural networks and their applications.",
                "sources": [
                    {
                        "documentId": "550e8400-e29b-41d4-a716-446655440000",
                        "fileName": "ai_guide.pdf",
                        "page": 12,
                        "source": "text"
                    },
                    {
                        "documentId": "550e8400-e29b-41d4-a716-446655440001", 
                        "fileName": "ml_algorithms.pdf",
                        "page": 3,
                        "source": "image"
                    }
                ]
            }
        }


@router.post(
    "/query", 
    response_model=ChatResponse, 
    status_code=status.HTTP_200_OK,
    summary="Ask Question",
    description="Ask a question about uploaded documents and get an AI-generated response"
)
async def chat_query(
    query: ChatQuery,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Process a chat query and generate a response based on uploaded documents.
    
    This endpoint retrieves relevant content from uploaded documents, generates
    an AI response based on the context, and saves the conversation history.
    
    Args:
        query: Chat query containing session ID and user message
        current_user: Authenticated user information (injected by dependency)
        
    Returns:
        ChatResponse: AI-generated answer with source document references
        
    Raises:
        HTTPException:
            - 404: Session not found or doesn't belong to user
            - 500: Error processing the query or generating response
    """
    # Verify session belongs to user
    session = astra_client.get_session(query.sessionId, current_user["userId"])
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or doesn't belong to user"
        )
    
    try:
        # Retrieve relevant documents
        retrieved_docs = rag_retriever.retrieve_relevant_docs(
            query.message,
            current_user["userId"],
            query.sessionId
        )
        
        # Format context for the prompt
        context = rag_retriever.format_context_for_prompt(retrieved_docs)
        
        # Get conversation history
        conversation_history = astra_client.get_session_messages(
            query.sessionId, 
            current_user["userId"]
        )
        
        # Generate response using RAG chain
        raw_answer = rag_chain.generate_response(
            query.message,
            context,
            conversation_history
        )
        
        # Sanitize answer for JSON serialization
        answer = sanitize_text_for_json(raw_answer)
        
        # Extract sources
        sources = rag_chain.extract_sources(retrieved_docs)
        
        # Save user message
        user_message = {
            "messageId": generate_uuid(),
            "userId": current_user["userId"],
            "sessionId": query.sessionId,
            "role": "user",
            "content": sanitize_text_for_json(query.message),
            "createdAt": get_current_timestamp()
        }
        astra_client.create_message(user_message)
        
        # Save assistant message
        assistant_message = {
            "messageId": generate_uuid(),
            "userId": current_user["userId"],
            "sessionId": query.sessionId,
            "role": "assistant",
            "content": answer,
            "createdAt": get_current_timestamp()
        }
        astra_client.create_message(assistant_message)
        
        # Format sources for response
        formatted_sources = [
            SourceInfo(
                documentId=source["documentId"],
                fileName=source["fileName"],
                page=source["page"],
                source=source["source"]
            )
            for source in sources
        ]
        
        return ChatResponse(
            answer=answer,
            sources=formatted_sources
        )
        
    except Exception as e:
        print(f"Error processing chat query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing chat query"
        )