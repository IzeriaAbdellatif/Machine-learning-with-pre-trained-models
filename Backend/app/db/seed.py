import json
from pathlib import Path
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job


async def seed_jobs_from_file(db: AsyncSession, file_path: str | Path):
    path = Path(file_path)
    if not path.exists():
        return 0

    data = json.loads(path.read_text(encoding="utf-8"))
    # data assumed to be a list of job dicts
    created = 0
    for item in data:
        # prepare fields mapping; ensure id exists
        job_id = item.get("id") or item.get("job_id") or item.get("jobId") or item.get("pk")
        if not job_id:
            # generate based on title+company
            job_id = f"{item.get('title','')}-{item.get('company','')}-{created}"
        # parse dates if present
        posted_at = item.get("posted_at") or item.get("postedAt") or item.get("date")
        deadline = item.get("deadline")
        try:
            posted_at_parsed = datetime.fromisoformat(posted_at) if posted_at else None
        except Exception:
            posted_at_parsed = None
        try:
            deadline_parsed = datetime.fromisoformat(deadline) if deadline else None
        except Exception:
            deadline_parsed = None

        required_skills = item.get("required_skills") or item.get("skills") or []
        if isinstance(required_skills, str):
            required_skills = [s.strip() for s in required_skills.split(",") if s.strip()]

        job_data: dict[str, Any] = {
            "id": str(job_id),
            "title": item.get("title") or item.get("job_title") or "",
            "company": item.get("company") or item.get("employer") or "",
            "location": item.get("location") or item.get("city") or "",
            "job_type": item.get("job_type") or item.get("type") or None,
            "experience_level": item.get("experience_level") or item.get("level") or None,
            "description": item.get("description") or item.get("summary") or None,
            "required_skills": required_skills,
            "salary_min": item.get("salary_min") or item.get("salary") or None,
            "salary_max": item.get("salary_max") or None,
            "currency": item.get("currency") or None,
            "posted_at": posted_at_parsed,
            "deadline": deadline_parsed,
        }

        # check if exists
        existing = await db.get(Job, str(job_id))
        if existing:
            continue
        job = Job(**job_data)
        db.add(job)
        created += 1
    if created > 0:
        await db.commit()
    return created
