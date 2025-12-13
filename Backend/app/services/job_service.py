from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.models import Job


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
