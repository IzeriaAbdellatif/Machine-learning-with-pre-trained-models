from fastapi import APIRouter, status, Query
from typing import Optional

from app.schemas.schemas import (
    JobResponse,
    JobsListResponse,
)


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get(
    "",
    response_model=JobsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Search jobs",
    responses={
        200: {"description": "Jobs list retrieved"},
        400: {"description": "Invalid search parameters"},
    },
)
async def search_jobs(
    title: Optional[str] = Query(None, description="Job title keyword"),
    location: Optional[str] = Query(None, description="Job location"),
    skills: Optional[list[str]] = Query(None, description="Required skills"),
    job_type: Optional[str] = Query(None, description="Employment type (Full-time, Part-time, etc.)"),
    experience_level: Optional[str] = Query(None, description="Experience level filter"),
    salary_min: Optional[float] = Query(None, ge=0, description="Minimum salary"),
    salary_max: Optional[float] = Query(None, ge=0, description="Maximum salary"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(10, ge=1, le=100, description="Pagination limit"),
) -> JobsListResponse:
    """
    Search for jobs with various filters.
    
    Query Parameters:
    - **title**: Filter by job title keyword
    - **location**: Filter by job location
    - **skills**: Filter by required skills (list of skills)
    - **job_type**: Filter by employment type
    - **experience_level**: Filter by required experience level
    - **salary_min**: Filter by minimum salary
    - **salary_max**: Filter by maximum salary
    - **skip**: Pagination offset (default: 0)
    - **limit**: Number of results per page (default: 10, max: 100)
    
    Returns paginated list of matching jobs.
    """
    pass


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get job details",
    responses={
        200: {"description": "Job details retrieved"},
        404: {"description": "Job not found"},
    },
)
async def get_job(job_id: str) -> JobResponse:
    """
    Get detailed information about a specific job.
    
    - **job_id**: The unique identifier of the job
    
    Returns complete job details including description, requirements, and compensation.
    """
    pass
