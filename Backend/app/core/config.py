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
    
    # Database (placeholder for future use)
    DATABASE_URL: str = "sqlite:///./test.db"

    DEBUG: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()
