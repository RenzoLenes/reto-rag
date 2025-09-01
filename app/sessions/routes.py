from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from core.security import get_current_user
from core.utils import generate_uuid, get_current_timestamp
from db.astra_client import astra_client
from sessions.models import SessionCreate, SessionOut
from schemas.responses import ErrorResponse

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