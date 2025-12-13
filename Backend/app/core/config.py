from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and environment variables."""
    
    # API Configuration
    API_TITLE: str = "Job Search API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "REST API for job search application"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - default to PostgreSQL async driver. Override via .env in production.
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/jobsdb"

    DEBUG: bool = False

    # GROQ LLM Service Configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    
    class Config:
        env_file = ".env"


settings = Settings()
