from typing import Optional, List,Literal
from pydantic import BaseModel
from datetime import date

class JobInput(BaseModel):
    """
    Représente une offre telle qu'elle sort du scraping / fichier JSON.
    Correspond aux clés de indeed_stages_data_ia.json.
    """
    search_keyword: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: str
    job_url: Optional[str] = None
    apply_url: Optional[str] = None
    extract_date: Optional[date] = None

class JobLLMOutput(BaseModel):
    """
    Sortie attendue du LLM pour une offre.
    """
    type_poste: Optional[Literal["stage", "emploi", "non_precise"]] = "non_precise"
    mode_travail: Optional[Literal["presentiel", "hybride", "remote", "non_precise"]] = "non_precise"
    competences_techniques: List[str] = []
    competences_soft: List[str] = []
    missions_principales: List[str] = []