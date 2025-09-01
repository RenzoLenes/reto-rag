from fastapi import APIRouter, HTTPException, status
from auth.models import UserCreate, UserLogin, UserOut, TokenResponse
from auth.service import auth_service
from schemas.responses import ErrorResponse

router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        409: {"model": ErrorResponse, "description": "User already exists"}
    }
)


@router.post(
    "/register", 
    response_model=UserOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account with email and password"
)
async def register(user_data: UserCreate):
    """
    Register a new user account.
    
    Args:
        user_data: User registration information including email and password
        
    Returns:
        UserOut: Created user information with userId and email
        
    Raises:
        HTTPException: 400 if user already exists or invalid data provided
    """
    try:
        return auth_service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login", 
    response_model=TokenResponse, 
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user and receive access token"
)
async def login(login_data: UserLogin):
    """
    Authenticate user and receive access token.
    
    Args:
        login_data: User login credentials (email and password)
        
    Returns:
        TokenResponse: Access token, token type, and expiration time
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    try:
        return auth_service.login_user(login_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )