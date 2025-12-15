# app/services/scoring_service.py

"""
Scoring service that wraps rule_scoring_service and provides clean interfaces
for computing and enriching jobs with relevance scores.

This service is responsible for:
- Converting database models to scoring-friendly dictionaries
- Computing rule-based and ML-based scores
- Enriching job responses with detailed score breakdowns
"""

from typing import Dict, List, Optional, Tuple
from app.models import User, Job
from app.schemas.user_profile import UserProfile
from app.services.rule_scoring_service import (
    compute_rule_scores_for_job,
    compute_final_score,
)


class ScoringService:
    """
    Service for computing job relevance scores based on user profile.
    Provides clean separation between scoring logic and API layer.
    """

    @staticmethod
    def _build_job_dict(job: Job) -> Dict:
        """
        Convert Job ORM model to dictionary compatible with rule_scoring_service.
        
        Args:
            job: Job ORM model from database
            
        Returns:
            Dictionary with job data in expected format for scoring
        """
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description or "",
            "competences_techniques": job.required_skills or [],
            "mode_travail": job.mode_travail or "",
            "remuneration": job.remuneration or "",
            "location": job.location,
            "score_embedding": job.score_embedding or 0.0,
            "missions_principales": job.missions_principales or [],
        }

    @staticmethod
    def _build_user_profile(user: User) -> Optional[UserProfile]:
        """
        Build UserProfile from User ORM model.
        
        If user hasn't set up their profile preferences, returns default profile.
        In a real system, you'd store UserProfile data in the database.
        
        Args:
            user: User ORM model from database
            
        Returns:
            UserProfile with user's preferences, or None if unavailable
        """
        # TODO: In production, store these preferences in User model or separate table
        # For now, return minimal profile - you should enhance this
        return UserProfile(
            target_job=getattr(user, "target_job", ""),
            skills=getattr(user, "skills", []),
            soft_skills=getattr(user, "soft_skills", []),
            preferred_locations=getattr(user, "preferred_locations", []),
            preferred_mode_travail=getattr(user, "preferred_mode_travail", []),
            min_remuneration=getattr(user, "min_remuneration", None),
            currency=getattr(user, "currency", "MAD"),
        )

    @staticmethod
    def compute_job_score(job: Job, user_profile: UserProfile) -> Dict:
        """
        Compute all scoring components for a single job given a user profile.
        
        Args:
            job: Job ORM model
            user_profile: User profile with preferences and skills
            
        Returns:
            Dictionary containing:
                - score_skills: Match between user skills and job requirements
                - score_mode_travail: Work mode compatibility
                - score_location: Location preference match
                - score_remuneration: Salary compatibility
                - score_embedding: Pre-computed embedding similarity
                - score_final: Weighted combined score
        """
        # Convert ORM models to dictionaries for rule scoring
        job_dict = ScoringService._build_job_dict(job)

        # Compute rule-based scores
        rule_scores = compute_rule_scores_for_job(job_dict, user_profile)

        # Fuse with embedding score and compute final score
        final_score, score_details = compute_final_score(job_dict, rule_scores)

        return score_details

    @staticmethod
    def enrich_job_with_score(job: Job, user_profile: UserProfile) -> Dict:
        """
        Enrich a Job ORM model with computed scores for API response.
        
        Args:
            job: Job ORM model
            user_profile: User profile with preferences
            
        Returns:
            Dictionary with job data and computed scores for API response
        """
        score_details = ScoringService.compute_job_score(job, user_profile)

        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "experience_level": job.experience_level,
            "description": job.description,
            "required_skills": job.required_skills or [],
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "currency": job.currency,
            "posted_at": job.posted_at,
            "deadline": job.deadline,
            "job_url": job.job_url,
            "apply_url": job.apply_url,
            "mode_travail": job.mode_travail,
            "remuneration": job.remuneration,
            "missions_principales": job.missions_principale or [],
            "search_keyword": job.search_keyword,
            # Scoring details
            "score": {
                "skills": score_details.get("score_skills", 0.0),
                "mode_travail": score_details.get("score_mode_travail", 0.0),
                "location": score_details.get("score_location", 0.0),
                "remuneration": score_details.get("score_remuneration", 0.0),
                "embedding": score_details.get("score_embedding", 0.0),
                "final": score_details.get("score_final", 0.0),
            },
        }

    @staticmethod
    def enrich_jobs_with_scores(
        jobs: List[Job], user_profile: UserProfile
    ) -> List[Dict]:
        """
        Enrich multiple jobs with computed scores.
        
        Args:
            jobs: List of Job ORM models
            user_profile: User profile with preferences
            
        Returns:
            List of enriched job dictionaries sorted by final score (descending)
        """
        enriched_jobs = [
            ScoringService.enrich_job_with_score(job, user_profile) for job in jobs
        ]

        # Sort by final score in descending order
        enriched_jobs.sort(key=lambda x: x["score"]["final"], reverse=True)

        return enriched_jobs
