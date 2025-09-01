from typing import Optional, Dict, Any
from core.security import hash_password, verify_password, create_jwt_token
from core.utils import generate_uuid, get_current_timestamp
from core.config import settings
from db.astra_client import astra_client
from auth.models import UserCreate, UserLogin, UserOut, TokenResponse


class AuthService:
    
    def register_user(self, user_data: UserCreate) -> UserOut:
        existing_user = astra_client.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        user_id = generate_uuid()
        password_hash = hash_password(user_data.password)
        
        user_doc = {
            "userId": user_id,
            "email": user_data.email,
            "passwordHash": password_hash,
            "createdAt": get_current_timestamp()
        }
        
        astra_client.create_user(user_doc)
        
        return UserOut(userId=user_id, email=user_data.email)
    
    def login_user(self, login_data: UserLogin) -> TokenResponse:
        user = astra_client.get_user_by_email(login_data.email)
        if not user:
            raise ValueError("Invalid email or password")
        
        if not verify_password(login_data.password, user["passwordHash"]):
            raise ValueError("Invalid email or password")
        
        token_data = {
            "userId": user["userId"],
            "email": user["email"]
        }
        
        access_token = create_jwt_token(token_data)
        
        return TokenResponse(
            accessToken=access_token,
            expiresIn=settings.jwt_expires_seconds
        )


auth_service = AuthService()