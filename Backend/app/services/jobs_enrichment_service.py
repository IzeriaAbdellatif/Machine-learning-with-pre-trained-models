# app/services/jobs_enrichment_service.py

import json
import time
from pathlib import Path
from typing import List

from app.schemas.jobs import JobInput, JobLLMOutput
from app.services.LLM_service import call_llm


def build_job_text(job: JobInput) -> str:
    """
    Construit un texte simple pour le LLM à partir d'un JobInput.
    """
    parts = [
        f"Titre : {job.title}",
        f"Entreprise : {job.company or 'Non précisée'}",
        f"Lieu : {job.location or 'Non précisé'}",
        "",
        "Description :",
        job.description or "",
    ]
    return "\n".join(parts)


def build_prompt(job_text: str) -> str:
    """
    Prompt simple qui force le format JSON.
    """
    return f"""
Tu es un assistant spécialisé en analyse d'offres d'emploi et de stage.

On te fournit le texte complet d'une offre (titre, entreprise, lieu, description).
Ta mission est d'extraire des informations structurées.

TÂCHES :
1. Déterminer le type de poste :
   - "stage" si c'est clairement un stage (Stage, Internship, PFE, etc.)
   - "emploi" si c'est un poste salarié (CDI, CDD, etc.)
   - "non_precise" si tu ne peux pas savoir.

2. Déterminer le mode de travail :
   - "remote" si le travail est à distance / télétravail.
   - "hybride" si c'est un mélange présentiel + télétravail.
   - "presentiel" si le travail est sur site.
   - "non_precise" si ce n'est pas clair.

3. Extraire une liste de compétences techniques (ex: Python, SQL, Machine Learning,
   Power BI, Docker, Linux, etc.).

4. Extraire une liste de compétences comportementales (soft skills)
   (ex: travail en équipe, communication, autonomie, etc.).

5. Résumer les missions principales du poste sous forme d'une liste de 3 à 7
   phrases courtes (chaque phrase = une mission).

6. Extraire une liste de compétences "nice to have" (appréciées mais non obligatoires),
   si elles sont mentionnées explicitement comme un plus ou souhaitables.
   Exemple : "serait un plus", "souhaité", "optionnel".

7. Extraire la rémunération ou le salaire si elle est mentionnée :
   - par exemple "10 000 MAD brut", "entre 35k et 45k EUR/an", "stage rémunéré 3 000 MAD/mois".
   - S'il n'y a aucune information claire sur le salaire, mets une chaîne vide "".

FORMAT DE RÉPONSE :
Tu DOIS répondre STRICTEMENT en JSON valide, sans aucun texte avant ou après.
Utilise exactement cette structure :

{{
  "type_poste": "stage" | "emploi" | "non_precise",
  "mode_travail": "presentiel" | "hybride" | "remote" | "non_precise",
  "competences_techniques": ["...", "..."],
  "competences_soft": ["...", "..."],
  "nice_to_have_skills": ["...", "..."],
  "remuneration": "texte du salaire ou \"\" s'il n'y a rien",
  "missions_principales": ["...", "...", "..."]
}}

TEXTE DE L'OFFRE :
--------------------
{job_text}
--------------------
"""


def parse_llm_json(raw: str) -> dict:
    """
    Essaie de parser la réponse LLM en JSON.
    Si ça rate, renvoie un dict vide (Pydantic gérera avec les valeurs par défaut).
    """
    raw = raw.strip()

    # Essai direct
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Essai avec extraction entre { ... }
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            pass

    print("[WARN] Impossible de parser la réponse LLM, on utilise un dict vide.")
    return {}


def enrich_one_job(job: JobInput) -> JobLLMOutput:
    """
    Enrichit une seule offre via le LLM (Groq).
    """
    job_text = build_job_text(job)
    prompt = build_prompt(job_text)

    raw_content = call_llm(prompt)
    data = parse_llm_json(raw_content)

    try:
        return JobLLMOutput(**data)
    except Exception as e:
        print("[WARN] Erreur de validation Pydantic sur JobLLMOutput :", e)
        return JobLLMOutput()  # tout par défaut


def enrich_jobs_from_file(
    input_path: str = "indeed_stages_data_ia.json",
    output_path: str = "indeed_stages_data_ia_enriched.json",
    max_jobs: int | None = None,
) -> None:
    """
    Lit un fichier JSON d'offres, enrichit chaque offre avec le LLM,
    et écrit un nouveau JSON enrichi.
    max_jobs permet de limiter le nombre d'offres (utile pour tests).
    """
    in_path = Path(input_path)
    out_path = Path(output_path)

    if not in_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {in_path.resolve()}")

    print(f"Chargement de {in_path} ...")
    raw_list = json.loads(in_path.read_text(encoding="utf-8"))

    if max_jobs is not None:
        raw_list = raw_list[:max_jobs]

    jobs: List[JobInput] = [JobInput(**item) for item in raw_list]
    print(f"Enrichissement de {len(jobs)} offres ...")

    enriched: List[dict] = []

    for idx, job in enumerate(jobs, start=1):
        print(f"[INFO] Traitement offre {idx}/{len(jobs)} : {job.title[:60]}...")
        llm_out = enrich_one_job(job)

        merged = {
            **job.model_dump(),
            **llm_out.model_dump(),
        }
        enriched.append(merged)

        # petite pause pour être gentil avec l'API (facultatif)
        time.sleep(0.5)

    # IMPORTANT : default=str pour les dates, etc.
    out_path.write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"✅ Fichier écrit : {out_path.resolve()}")


if __name__ == "__main__":
    # Script simple : traite 10 offres (change max_jobs si tu veux tout traiter)
    enrich_jobs_from_file(
        input_path="app/services/indeed_stages_data_ia.json",
        output_path="app/services/indeed_stages_data_ia_enriched.json",
        max_jobs=None,  # mets None pour tout traiter
    )
