# app/schemas/user_profile.py

from typing import List, Optional
from pydantic import BaseModel


class UserProfile(BaseModel):
    """
    Profil utilisateur utilisé pour le matching via embeddings + règles.
    """
    target_job: str
    skills: List[str]                      # compétences techniques principales
    soft_skills: List[str] = []            # soft skills (optionnel)
    preferred_locations: List[str] = []    # ex: ["Casablanca", "Rabat", "Remote"]
    preferred_mode_travail: List[str] = [] # ex: ["remote", "hybride"]
    min_remuneration: Optional[float] = None  # ex: 8000 (mensuel, approx)
    currency: Optional[str] = "MAD"
