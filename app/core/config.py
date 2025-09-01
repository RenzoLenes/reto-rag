from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # FastAPI
    app_env: str = "dev"
    app_port: int = 8000
    jwt_secret: str
    jwt_expires_seconds: int = 86400
    
    # OpenAI
    openai_api_key: str
    
    # AWS S3
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_s3_region: str = "us-east-1"
    aws_s3_bucket: str
    
    # AstraDB
    astra_db_api_endpoint: str
    astra_db_application_token: str
    astra_db_keyspace: str = "default_keyspace"
    astra_db_collection_users: str = "users"
    astra_db_collection_sessions: str = "sessions"
    astra_db_collection_documents: str = "documents"
    astra_db_collection_embeddings: str = "embeddings"
    astra_db_collection_messages: str = "messages"

    class Config:
        # Find .env file in parent directory of app
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = False


settings = Settings()