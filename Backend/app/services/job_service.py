from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Tuple
from datetime import datetime

from app.models import Job, User
from app.schemas.user_profile import UserProfile


async def get_job_by_id(db: AsyncSession, job_id: str) -> Optional[Job]:
    result = await db.execute(select(Job).where(Job.id == job_id))
    return result.scalars().first()


async def create_job(db: AsyncSession, job_data: dict) -> Job:
    job = Job(**job_data)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def search_jobs(
    db: AsyncSession,
    title: Optional[str] = None,
    location: Optional[str] = None,
    skills: Optional[List[str]] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    skip: int = 0,
    limit: int = 10,
):
    query = select(Job)
    filters = []

    if title:
        filters.append(Job.title.ilike(f"%{title}%"))
    if location:
        filters.append(Job.location.ilike(f"%{location}%"))
    if job_type:
        filters.append(Job.job_type == job_type)
    if experience_level:
        filters.append(Job.experience_level == experience_level)
    if salary_min is not None:
        filters.append(Job.salary_min >= salary_min)
    if salary_max is not None:
        filters.append(Job.salary_max <= salary_max)
    if skills:
        # simple containment check for JSONB - check any overlap
        for skill in skills:
            filters.append(Job.required_skills.contains([skill]))

    if filters:
        query = query.where(and_(*filters))

    total = await db.execute(select(Job).where(and_(*filters)) if filters else select(Job))
    total_count = len(total.scalars().all())

    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()

    return items, total_count


async def get_all_jobs(db: AsyncSession, skip: int = 0, limit: int = 10) -> Tuple[List[Job], int]:
    """
    Retrieve all jobs from the database with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination offset)
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (list of Job objects, total count of all jobs)
    """
    # Get total count
    total_query = await db.execute(select(Job))
    total_count = len(total_query.scalars().all())

    # Get paginated results
    query = await db.execute(
        select(Job).offset(skip).limit(limit)
    )
    items = query.scalars().all()

    return items, total_count


async def get_jobs_with_scores(
    db: AsyncSession,
    user: User,
    skip: int = 0,
    limit: int = 10,
) -> Tuple[List[Dict], int]:
    """
    Retrieve all jobs and enrich them with relevance scores for the authenticated user.
    
    This function:
    1. Fetches all jobs from database
    2. Builds user profile from user data
    3. Computes relevance scores for each job
    4. Returns enriched jobs sorted by final score (descending)
    
    Args:
        db: Database session
        user: Authenticated User ORM model
        skip: Number of records to skip (pagination offset)
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (list of enriched job dicts with scores, total count)
        
    Raises:
        ImportError: If scoring service cannot be imported
    """
    from app.services.scoring_service import ScoringService

    # Fetch all jobs
    jobs, total_count = await get_all_jobs(db, skip=skip, limit=limit)

    if not jobs:
        return [], total_count

    # Build user profile from user data
    # NOTE: UserProfile is built from User attributes
    # In production, consider storing profile preferences in a separate table
    user_profile = ScoringService._build_user_profile(user)

    if not user_profile:
        # If profile cannot be built, return jobs without scores
        return [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "score": {"final": 0.0},
            }
            for job in jobs
        ], total_count

    # Enrich jobs with scores
    enriched_jobs = ScoringService.enrich_jobs_with_scores(jobs, user_profile)

    return enriched_jobs, total_count
