from fastapi import APIRouter, status, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.schemas import (
    SavedJobRequest,
    SavedJobResponse,
    SavedJobsListResponse,
    MessageResponse,
)
from app.core.security import get_current_user
from app.db.session import get_session
from app.services import saved_job_service
from app.services.scoring import scoring_function
from app.models import User


router = APIRouter(prefix="/saved-jobs", tags=["Saved Jobs"])


@router.post(
    "/{job_id}",
    response_model=SavedJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a job",
    responses={
        201: {"description": "Job successfully saved"},
        400: {"description": "Job already saved or invalid job ID"},
        401: {"description": "Unauthorized"},
        404: {"description": "Job not found"},
    },
)
async def save_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> SavedJobResponse:
    """
    Save a job for the authenticated user.
    
    - **job_id**: The unique identifier of the job to save
    
    Requires valid JWT token. Returns the saved job with metadata.
    """
    user_id = current_user.get("sub")
    saved = await saved_job_service.save_job_for_user(db, user_id, job_id)
    # Add dynamic score for the saved job when available
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user and saved.job:
        saved.job.score = scoring_function(user, saved.job)
    return saved


@router.get(
    "",
    response_model=SavedJobsListResponse,
    status_code=status.HTTP_200_OK,
    summary="List saved jobs",
    responses={
        200: {"description": "Saved jobs list retrieved"},
        401: {"description": "Unauthorized"},
    },
)
async def list_saved_jobs(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(10, ge=1, le=100, description="Pagination limit"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> SavedJobsListResponse:
    """
    Get all saved jobs for the authenticated user.
    
    Query Parameters:
    - **skip**: Pagination offset (default: 0)
    - **limit**: Number of results per page (default: 10, max: 100)
    
    Requires valid JWT token. Returns paginated list of user's saved jobs.
    """
    user_id = current_user.get("sub")
    items, total = await saved_job_service.list_saved_jobs_for_user(db, user_id, skip=skip, limit=limit)
    # Apply scores to each saved job when user profile is available
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user:
        for saved_job in items:
            if saved_job.job:
                saved_job.job.score = scoring_function(user, saved_job.job)
    return SavedJobsListResponse(items=items, total=total, skip=skip, limit=limit)


@router.delete(
    "/{job_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove saved job",
    responses={
        200: {"description": "Job successfully removed from saved"},
        401: {"description": "Unauthorized"},
        404: {"description": "Saved job not found"},
    },
)
async def remove_saved_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """
    Remove a job from the authenticated user's saved jobs.
    
    - **job_id**: The unique identifier of the job to remove
    
    Requires valid JWT token. Returns confirmation message.
    """
    user_id = current_user.get("sub")
    await saved_job_service.remove_saved_job(db, user_id, job_id)
    return MessageResponse(message="Saved job removed")
