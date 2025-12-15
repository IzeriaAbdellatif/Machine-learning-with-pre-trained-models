# app/services/scoring.py

"""
Scoring service: Computes job relevance scores dynamically at request time.

This module provides a single, focused scoring_function that evaluates
how well a job matches a user's profile without any database persistence.

Design (inspired by rule_scoring_service):
- Pure function: scoring_function(user, job) -> float
- Combines embedding score with rule-based sub-scores
- No caching, no database storage
- Easy to tweak weights and factors
"""

import re
from typing import Optional, List, Set
from app.models import User, Job


def _parse_comma_separated(value: Optional[str]) -> List[str]:
    """Parse comma-separated string into list of cleaned items."""
    if not value:
        return []
    return [item.strip().lower() for item in value.split(',') if item.strip()]


def _normalize_token(value: str) -> str:
    """Normalize a token for fuzzy comparisons."""
    return value.strip().lower()


def _extract_skills(user: User) -> Set[str]:
    """Extract all skills from user profile (skills field)."""
    skills = set()
    
    # From skills field (comma-separated)
    if hasattr(user, 'skills') and user.skills:
        skills.update(_parse_comma_separated(user.skills))
    
    return skills


def _extract_job_skills(job: Job) -> Set[str]:
    """Extract skills from job (required_skills, title, description)."""
    skills = set()
    
    # From required_skills array
    if job.required_skills:
        skills.update([s.lower() for s in job.required_skills])

    
    return skills


def _compute_skill_score(user: User, job: Job) -> float:
    """Compute skill overlap score in [0,1]."""
    user_skills = [_normalize_token(s) for s in _extract_skills(user)]
    job_skills = [_normalize_token(s) for s in _extract_job_skills(job)]

    if not user_skills or not job_skills:
        return 0.0

    match_count = 0
    for us in user_skills:
        for js in job_skills:
            if us in js or js in us:
                match_count += 1
                break

    return min(1.0, match_count / len(job_skills))


def _compute_mode_travail_score(user: User, job: Job) -> float:
    """Score work-mode compatibility in [0,1]."""
    preferred_modes = [_normalize_token(m) for m in _parse_comma_separated(getattr(user, 'preferred_mode_travail', None))]
    job_mode = _normalize_token(job.mode_travail or "")

    if not preferred_modes or not job_mode:
        return 0.0

    if job_mode in preferred_modes:
        return 1.0

    if job_mode == "presentiel" and ("remote" in preferred_modes or "hybride" in preferred_modes):
        return 0.2

    return 0.5


def _compute_location_score(user: User, job: Job) -> float:
    """Score location alignment in [0,1] using substring matches."""
    preferred_locations = [_normalize_token(loc) for loc in _parse_comma_separated(getattr(user, 'preferred_locations', None))]
    if not preferred_locations and getattr(user, 'location', None):
        preferred_locations = [_normalize_token(user.location)]
    job_loc = _normalize_token(job.location or "")

    if not preferred_locations or not job_loc:
        return 0.0

    for loc in preferred_locations:
        if loc and loc in job_loc:
            return 1.0

    return 0.0


def _extract_numeric_remuneration(remu_text: str) -> float:
    """Extract a numeric remuneration signal from free text."""
    if not remu_text:
        return 0.0

    nums = re.findall(r"\d+(?:[.,]\d+)?", remu_text)
    values = []
    for n in nums:
        n = n.replace(",", ".")
        try:
            values.append(float(n))
        except ValueError:
            continue

    return max(values) if values else 0.0


def _compute_remuneration_score(user: User, job: Job) -> float:
    """Score salary compatibility in [0,1]."""
    min_remu = getattr(user, 'min_remuneration', None)
    try:
        min_remu = float(min_remu) if min_remu is not None else None
    except (ValueError, TypeError):
        min_remu = None
    if min_remu is None:
        return 0.0

    # Prefer structured salary when available
    if job.salary_min is not None:
        if job.salary_min >= min_remu:
            return 1.0
        if job.salary_min >= 0.7 * min_remu:
            return 0.5
        return 0.0

    if job.salary_max is not None:
        if job.salary_max >= min_remu:
            return 0.8
        if job.salary_max >= 0.7 * min_remu:
            return 0.4
        return 0.0

    remu_val = _extract_numeric_remuneration(job.remuneration or "")
    if remu_val <= 0:
        return 0.0

    if remu_val >= min_remu:
        return 1.0
    if remu_val >= 0.7 * min_remu:
        return 0.5
    return 0.0


def scoring_function(user: User, job: Job) -> float:
    """
    Compute job relevance score for a user.

    Inspired by rule_scoring_service: mix embedding with rule-based scores.
    Weights sum to 1.0 to keep output in [0,1].
    - 0.55 * embedding (job.score_embedding or 0)
    - 0.25 * skill_score (overlap ratio)
    - 0.10 * mode_travail_score
    - 0.05 * location_score
    - 0.05 * remuneration_score
    """

    embedding_score = float(job.score_embedding or 0.0)
    skill_score = _compute_skill_score(user, job)
    mode_score = _compute_mode_travail_score(user, job)
    location_score = _compute_location_score(user, job)
    remuneration_score = _compute_remuneration_score(user, job)

    final_score = (
        0.55 * embedding_score
        + 0.25 * skill_score
        + 0.10 * mode_score
        + 0.05 * location_score
        + 0.05 * remuneration_score
    )

    return min(1.0, max(0.0, final_score))
