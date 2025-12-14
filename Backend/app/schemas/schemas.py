from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ============================================================================
# Authentication Schemas
# ============================================================================

class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=72, description="User password (min 8, max 72 chars)")
    name: str = Field(..., min_length=1, description="User full name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123",
                "name": "John Doe"
            }
        }


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., max_length=72, description="User password (max 72 chars)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123"
            }
        }


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: "UserResponse" = Field(..., description="User information")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra" : {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "name": "John Doe"
                }
            }
        }
}


class LogoutResponse(BaseModel):
    """Schema for logout response."""
    message: str = Field(default="Successfully logged out", description="Logout confirmation message")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "message": "Successfully logged out"
            }
        }
}


# ============================================================================
# User Profile Schemas
# ============================================================================

class UserResponse(BaseModel):
    """Schema for user profile response."""
    id: str = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., description="User full name")
    phone: Optional[str] = Field(None, description="User phone number")
    location: Optional[str] = Field(None, description="User location")
    bio: Optional[str] = Field(None, description="User bio/summary")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "John Doe",
                "phone": "+1234567890",
                "location": "San Francisco, CA",
                "bio": "Software engineer with 5 years experience",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T15:45:00Z"
            }
        }
}


class UserUpdateRequest(BaseModel):
    """Schema for user profile update request."""
    name: Optional[str] = Field(None, description="User full name")
    phone: Optional[str] = Field(None, description="User phone number")
    location: Optional[str] = Field(None, description="User location")
    bio: Optional[str] = Field(None, description="User bio/summary")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "name": "John Doe",
                "phone": "+1234567890",
                "location": "San Francisco, CA",
                "bio": "Software engineer with 5 years experience"
            }
        }
}


# ============================================================================
# Job Schemas
# ============================================================================

class JobResponse(BaseModel):
    """Schema for job listing response."""
    id: str = Field(..., description="Job unique identifier")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    job_type: Optional[str] = Field(None, description="Employment type (Full-time, Part-time, etc.)")
    experience_level: Optional[str] = Field(None, description="Required experience level")
    description: Optional[str] = Field(None, description="Job description")
    required_skills: list[str] = Field(default=[], description="List of required skills")
    salary_min: Optional[float] = Field(None, description="Minimum salary")
    salary_max: Optional[float] = Field(None, description="Maximum salary")
    currency: Optional[str] = Field(None, description="Salary currency")
    posted_at: Optional[datetime] = Field(None, description="Job posting timestamp")
    deadline: Optional[datetime] = Field(None, description="Application deadline")
    
    # Indeed-specific fields
    job_url: Optional[str] = Field(None, description="Job posting URL")
    apply_url: Optional[str] = Field(None, description="Direct application URL")
    mode_travail: Optional[str] = Field(None, description="Work mode (remote/hybrid/presentiel)")
    remuneration: Optional[str] = Field(None, description="Salary information (text)")
    missions_principales: Optional[list[str]] = Field(None, description="Main missions/tasks")
    search_keyword: Optional[str] = Field(None, description="Search keyword")
    
    # ML scoring fields
    score_embedding: Optional[float] = Field(None, description="Embedding similarity score")
    score_final: Optional[float] = Field(None, description="Final ranking score")
    score_cross_encoder: Optional[float] = Field(None, description="Cross-encoder reranking score")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "id": "job123",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "job_type": "Full-time",
                "experience_level": "Senior",
                "description": "We are looking for a senior Python developer...",
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "salary_min": 150000,
                "salary_max": 200000,
                "currency": "USD",
                "posted_at": "2024-01-15T10:30:00Z",
                "deadline": "2024-02-15T23:59:59Z",
                "job_url": "https://example.com/job/123",
                "apply_url": "https://example.com/apply/123",
                "mode_travail": "remote",
                "remuneration": "stage rémunéré",
                "missions_principales": ["Develop features", "Code review"],
                "search_keyword": "Python Developer",
                "score_embedding": 0.85,
                "score_final": 0.78,
                "score_cross_encoder": 1.2
            }
        }
}


class JobSearchQuery(BaseModel):
    """Schema for job search query parameters."""
    title: Optional[str] = Field(None, description="Job title keyword")
    location: Optional[str] = Field(None, description="Job location")
    skills: Optional[list[str]] = Field(None, description="Required skills (filter jobs containing any)")
    job_type: Optional[str] = Field(None, description="Employment type filter")
    experience_level: Optional[str] = Field(None, description="Experience level filter")
    salary_min: Optional[float] = Field(None, description="Minimum salary filter")
    salary_max: Optional[float] = Field(None, description="Maximum salary filter")
    skip: Optional[int] = Field(default=0, ge=0, description="Pagination offset")
    limit: Optional[int] = Field(default=10, ge=1, le=100, description="Pagination limit")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "title": "Python Developer",
                "location": "San Francisco",
                "skills": ["Python", "FastAPI"],
                "job_type": "Full-time",
                "experience_level": "Senior",
                "salary_min": 100000,
                "salary_max": 300000,
                "skip": 0,
                "limit": 20
            }
        }
}


class JobsListResponse(BaseModel):
    """Schema for paginated jobs list response."""
    items: list[JobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs matching criteria")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "items": [
                    {
                        "id": "job123",
                        "title": "Senior Python Developer",
                        "company": "Tech Corp",
                        "location": "San Francisco, CA",
                        "job_type": "Full-time",
                        "experience_level": "Senior",
                        "description": "We are looking for a senior Python developer...",
                        "required_skills": ["Python", "FastAPI"],
                        "salary_min": 150000,
                        "salary_max": 200000,
                        "currency": "USD",
                        "posted_at": "2024-01-15T10:30:00Z",
                        "deadline": "2024-02-15T23:59:59Z"
                    }
                ],
                "total": 45,
                "skip": 0,
                "limit": 10
            }
        }
}


# ============================================================================
# Saved Jobs Schemas
# ============================================================================

class SavedJobRequest(BaseModel):
    """Schema for saving a job request."""
    job_id: str = Field(..., description="ID of the job to save")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "job_id": "job123"
            }
        }
}


class SavedJobResponse(BaseModel):
    """Schema for saved job response."""
    id: int = Field(..., description="Saved job unique identifier")
    user_id: str = Field(..., description="User ID who saved the job")
    job: JobResponse = Field(..., description="Full job details")
    saved_at: Optional[datetime] = Field(None, description="When the job was saved")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "id": 1,
                "user_id": "user123",
                "job": {
                    "id": "job123",
                    "title": "Senior Python Developer",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "job_type": "Full-time",
                    "experience_level": "Senior",
                    "description": "We are looking for a senior Python developer...",
                    "required_skills": ["Python", "FastAPI"],
                    "salary_min": 150000,
                    "salary_max": 200000,
                    "currency": "USD",
                    "posted_at": "2024-01-15T10:30:00Z",
                    "deadline": "2024-02-15T23:59:59Z"
                },
                "saved_at": "2024-01-20T14:30:00Z"
            }
        }
}


class SavedJobsListResponse(BaseModel):
    """Schema for paginated saved jobs list response."""
    items: list[SavedJobResponse] = Field(..., description="List of saved jobs")
    total: int = Field(..., description="Total number of saved jobs")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "user_id": "user123",
                        "job": {
                            "id": "job123",
                            "title": "Senior Python Developer",
                            "company": "Tech Corp",
                            "location": "San Francisco, CA",
                            "job_type": "Full-time",
                            "experience_level": "Senior",
                            "description": "We are looking for a senior Python developer...",
                            "required_skills": ["Python", "FastAPI"],
                            "salary_min": 150000,
                            "salary_max": 200000,
                            "currency": "USD",
                            "posted_at": "2024-01-15T10:30:00Z",
                            "deadline": "2024-02-15T23:59:59Z"
                        },
                        "saved_at": "2024-01-20T14:30:00Z"
                    }
                ],
                "total": 15,
                "skip": 0,
                "limit": 10
            }
        }
}


# ============================================================================
# Generic Response Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str = Field(..., description="Response message")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "message": "Operation successful"
            }
        }
}


class ErrorResponse(BaseModel):
    """Generic error response schema."""
    detail: str = Field(..., description="Error detail message")
    
    model_config = {
        "from_attributes": True,
                "json_schema_extra" : {
            "example": {
                "detail": "Resource not found"
            }
        }
}

TokenResponse.model_rebuild()
UserResponse.model_rebuild()
