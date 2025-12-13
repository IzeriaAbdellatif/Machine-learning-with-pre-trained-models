from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models import SavedJob, Job


async def get_saved_by_user_and_job(db: AsyncSession, user_id: str, job_id: str):
    result = await db.execute(select(SavedJob).where(SavedJob.user_id == user_id, SavedJob.job_id == job_id))
    return result.scalars().first()


async def save_job_for_user(db: AsyncSession, user_id: str, job_id: str):
    # ensure job exists
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalars().first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    existing = await get_saved_by_user_and_job(db, user_id, job_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job already saved")

    saved = SavedJob(user_id=user_id, job_id=job_id)
    db.add(saved)
    await db.commit()
    await db.refresh(saved)
    return saved


async def list_saved_jobs_for_user(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 10):
    result = await db.execute(select(SavedJob).where(SavedJob.user_id == user_id).offset(skip).limit(limit))
    items = result.scalars().all()
    total_res = await db.execute(select(SavedJob).where(SavedJob.user_id == user_id))
    total = len(total_res.scalars().all())
    return items, total


async def remove_saved_job(db: AsyncSession, user_id: str, job_id: str):
    existing = await get_saved_by_user_and_job(db, user_id, job_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved job not found")
    await db.delete(existing)
    await db.commit()
    return True
