"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PERFO AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-Powered Accounts Payable Automation Platform"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = "postgresql://perfo:perfo123@db:5432/perfodb"

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4.1"
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"
    AZURE_OPENAI_MODEL: str = "gpt-4.1"

    # Qdrant Vector Database
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "invoices"

    # LlamaParse
    LLAMAPARSE_API_KEY: Optional[str] = None

    # Redis (for background tasks)
    REDIS_URL: str = "redis://redis:6379/0"

    # File Upload
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Agents Configuration
    TOUCHLESS_THRESHOLD: float = 0.95  # 95% confidence for touchless processing

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
