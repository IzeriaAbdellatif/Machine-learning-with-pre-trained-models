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
        # Use job_url as unique identifier for duplicate detection
        job_url = item.get("job_url")
        
        # Check if job already exists by job_url
        if job_url:
            from sqlalchemy import select
            existing = await db.execute(
                select(Job).where(Job.job_url == job_url)
            )
            if existing.scalars().first():
                continue  # Skip if already exists

        # Dates: use explicit fields or Indeed's extract_date as posted_at
        posted_at = item.get("posted_at") or item.get("postedAt") or item.get("date") or item.get("extract_date")
        deadline = item.get("deadline")
        try:
            posted_at_parsed = datetime.fromisoformat(posted_at) if posted_at else None
        except Exception:
            posted_at_parsed = None
        try:
            deadline_parsed = datetime.fromisoformat(deadline) if deadline else None
        except Exception:
            deadline_parsed = None

        # Skills: merge available arrays from Indeed structure
        required_skills = item.get("required_skills") or item.get("skills") or []
        competences_techniques = item.get("competences_techniques") or []
        competences_soft = item.get("competences_soft") or []
        nice_to_have = item.get("nice_to_have_skills") or []
        if isinstance(required_skills, str):
            required_skills = [s.strip() for s in required_skills.split(",") if s.strip()]
        # normalize to strings and merge unique
        def _as_list(values: Any) -> list[str]:
            if values is None:
                return []
            if isinstance(values, list):
                return [str(v).strip() for v in values if str(v).strip()]
            return [str(values).strip()] if str(values).strip() else []

        merged_skills = []
        for arr in (required_skills, competences_techniques, competences_soft, nice_to_have):
            for v in _as_list(arr):
                if v and v not in merged_skills:
                    merged_skills.append(v)

        # Job type: prefer Indeed's type_poste (e.g., "stage")
        job_type = item.get("job_type") or item.get("type") or item.get("type_poste")

        # Salary mapping: remuneration may be free text; store in currency None, salary fields None
        salary_min = item.get("salary_min") or item.get("salary")
        salary_max = item.get("salary_max")
        currency = item.get("currency")

        # Do NOT set id - let database auto-generate it
        job_data: dict[str, Any] = {
            "title": item.get("title") or item.get("job_title") or "",
            "company": item.get("company") or item.get("employer") or "",
            "location": item.get("location") or item.get("city") or "",
            "job_type": job_type,
            "experience_level": item.get("experience_level") or item.get("level") or None,
            "description": item.get("description") or item.get("summary") or None,
            "required_skills": merged_skills,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "currency": currency,
            "posted_at": posted_at_parsed,
            "deadline": deadline_parsed,
            # Indeed-specific fields
            "job_url": job_url,
            "apply_url": item.get("apply_url"),
            "mode_travail": item.get("mode_travail"),
            "remuneration": item.get("remuneration"),
            "missions_principales": item.get("missions_principales"),
            "search_keyword": item.get("search_keyword"),
            # ML scoring fields
            "score_embedding": item.get("score_embedding"),
            "score_final": item.get("score_final"),
            "score_cross_encoder": item.get("score_cross_encoder"),
        }

        job = Job(**job_data)
        db.add(job)
        created += 1
    if created > 0:
        await db.commit()
    return created
