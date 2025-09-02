from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from core.security import get_current_user
from core.utils import generate_uuid, get_current_timestamp
from db.astra_client import astra_client
from sessions.models import SessionCreate, SessionOut, SessionUpdateRequest
from schemas.responses import ErrorResponse, SessionDeleteResponse, DocumentListResponse, DocumentInfo, SessionMessagesResponse, MessageInfo

router = APIRouter(
    prefix="/sessions", 
    tags=["Sessions"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing token"},
        403: {"model": ErrorResponse, "description": "Forbidden - Access denied"},
        404: {"model": ErrorResponse, "description": "Session not found"}
    }
)


@router.post(
    "/", 
    response_model=SessionOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Create New Session",
    description="Create a new chat session for the authenticated user"
)
async def create_session(
    session_data: SessionCreate, 
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Create a new chat session.
    
    Args:
        session_data: Session creation data (name)
        current_user: Authenticated user information (injected by dependency)
        
    Returns:
        SessionOut: Created session information with ID, name, and creation timestamp
    """
    session_id = generate_uuid()
    session_doc = {
        "sessionId": session_id,
        "userId": current_user["userId"],
        "name": session_data.name,
        "createdAt": get_current_timestamp()
    }
    
    astra_client.create_session(session_doc)
    
    return SessionOut(
        sessionId=session_id,
        name=session_data.name,
        createdAt=session_doc["createdAt"]
    )


@router.get(
    "/", 
    response_model=List[SessionOut],
    summary="Get User Sessions",
    description="Retrieve all chat sessions for the authenticated user"
)
async def get_sessions(current_user: Dict[str, str] = Depends(get_current_user)):
    """
    Get all sessions for the authenticated user.
    
    Args:
        current_user: Authenticated user information (injected by dependency)
        
    Returns:
        List[SessionOut]: List of user's sessions with ID, name, and creation timestamp
    """
    sessions = astra_client.get_user_sessions(current_user["userId"])
    
    return [
        SessionOut(
            sessionId=session["sessionId"],
            name=session["name"],
            createdAt=session["createdAt"]
        )
        for session in sessions
    ]


@router.put(
    "/{session_id}",
    response_model=SessionOut,
    summary="Update Session Name",
    description="Update the name of an existing session"
)
async def update_session(
    session_id: str,
    session_update: SessionUpdateRequest,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Update the name of an existing session.
    
    Args:
        session_id: The ID of the session to update
        session_update: New session data
        current_user: Authenticated user information (injected by dependency)
        
    Returns:
        SessionOut: Updated session information
        
    Raises:
        HTTPException: 
            - 404: Session not found or doesn't belong to user
            - 500: Error updating session
    """
    # Verify session exists and belongs to user
    session = astra_client.get_session(session_id, current_user["userId"])
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or doesn't belong to user"
        )
    
    # Update session name
    success = astra_client.update_session_name(
        session_id, 
        current_user["userId"], 
        session_update.name
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session"
        )
    
    # Return updated session
    return SessionOut(
        sessionId=session_id,
        name=session_update.name,
        createdAt=session["createdAt"]
    )


@router.get(
    "/{session_id}/documents",
    response_model=DocumentListResponse,
    summary="Get Session Documents",
    description="Get all documents uploaded to a specific session"
)
async def get_session_documents(
    session_id: str,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Get all documents for a specific session.
    
    Args:
        session_id: The ID of the session
        current_user: Authenticated user information (injected by dependency)
        
    Returns:
        DocumentListResponse: List of documents in the session
        
    Raises:
        HTTPException: 
            - 404: Session not found or doesn't belong to user
    """
    # Verify session exists and belongs to user
    session = astra_client.get_session(session_id, current_user["userId"])
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or doesn't belong to user"
        )
    
    # Get documents for this session
    documents_data = astra_client.get_session_documents(session_id, current_user["userId"])
    
    # Format documents
    documents = [
        DocumentInfo(
            documentId=doc["documentId"],
            fileName=doc["fileName"],
            pages=doc["pages"],
            uploadedAt=doc["uploadedAt"],
            s3Key=doc["s3Key"]
        )
        for doc in documents_data
    ]
    
    return DocumentListResponse(
        sessionId=session_id,
        documents=documents,
        totalDocuments=len(documents)
    )


@router.get(
    "/{session_id}/messages",
    response_model=SessionMessagesResponse,
    summary="Get Session Messages",
    description="Get all chat messages for a specific session"
)
async def get_session_messages(
    session_id: str,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Get all chat messages for a specific session.
    
    Args:
        session_id: The ID of the session
        current_user: Authenticated user information (injected by dependency)
        
    Returns:
        SessionMessagesResponse: List of messages in the session ordered by creation time
        
    Raises:
        HTTPException: 
            - 404: Session not found or doesn't belong to user
    """
    # Verify session exists and belongs to user
    session = astra_client.get_session(session_id, current_user["userId"])
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or doesn't belong to user"
        )
    
    # Get messages for this session
    messages_data = astra_client.get_session_messages(session_id, current_user["userId"])
    
    # Format messages
    messages = [
        MessageInfo(
            messageId=msg["messageId"],
            role=msg["role"],
            content=msg["content"],
            createdAt=msg["createdAt"]
        )
        for msg in messages_data
    ]
    
    return SessionMessagesResponse(
        sessionId=session_id,
        messages=messages,
        totalMessages=len(messages)
    )


@router.delete(
    "/{session_id}",
    response_model=SessionDeleteResponse,
    summary="Delete Session",
    description="Delete a session and all its related data (documents, embeddings, messages)"
)
async def delete_session(
    session_id: str,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Delete a session and all its related data.
    
    This endpoint will delete:
    - The session itself
    - All documents uploaded to this session
    - All embeddings generated from these documents
    - All chat messages in this session
    
    Args:
        session_id: The ID of the session to delete
        current_user: Authenticated user information (injected by dependency)
        
    Returns:
        SessionDeleteResponse: Deletion summary with counts of deleted items
        
    Raises:
        HTTPException: 
            - 404: Session not found or doesn't belong to user
            - 500: Error during deletion process
    """
    # Verify session exists and belongs to user
    session = astra_client.get_session(session_id, current_user["userId"])
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or doesn't belong to user"
        )
    
    try:
        # Delete all related data
        documents_deleted = astra_client.delete_session_documents(session_id, current_user["userId"])
        embeddings_deleted = astra_client.delete_session_embeddings(session_id, current_user["userId"])
        messages_deleted = astra_client.delete_session_messages(session_id, current_user["userId"])
        
        # Finally delete the session itself
        session_deleted = astra_client.delete_session(session_id, current_user["userId"])
        
        if not session_deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete session"
            )
        
        return SessionDeleteResponse(
            message="Session and all related data deleted successfully",
            sessionId=session_id,
            documentsDeleted=documents_deleted,
            embeddingsDeleted=embeddings_deleted,
            messagesDeleted=messages_deleted
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting session and related data"
        )