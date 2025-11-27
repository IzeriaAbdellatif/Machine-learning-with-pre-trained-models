from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, users, jobs, saved_jobs


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(saved_jobs.router)


@app.get(
    "/",
    tags=["Health Check"],
    summary="Health check endpoint",
    response_description="API is healthy",
)
async def root():
    """
    Root endpoint to verify API is running.
    
    Returns:
        Dictionary with status message and API version
    """
    return {
        "message": "Job Search API is running",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["Health Check"],
    summary="Health check",
    response_description="API health status",
)
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        Dictionary with status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
