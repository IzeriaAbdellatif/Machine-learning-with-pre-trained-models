# app/services/rule_scoring_service.py

import json
import re
from pathlib import Path
from typing import List, Tuple

from app.schemas.user_profile import UserProfile


# ------------------ Utilitaires profil & chargement ------------------ #

def load_user_profile(path: str = "user_profile.json") -> UserProfile:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Fichier profil introuvable : {p.resolve()}")
    data = json.loads(p.read_text(encoding="utf-8"))
    return UserProfile(**data)


def load_jobs(path: str) -> List[dict]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Fichier d'offres introuvable : {p.resolve()}")
    return json.loads(p.read_text(encoding="utf-8"))


# ------------------ 1. Score de skills ------------------ #

def normalize_token(s: str) -> str:
    return s.strip().lower()


def compute_skill_score(job: dict, profile: UserProfile) -> float:
    """
    Score basé sur le recoupement entre les skills du user et les
    competences_techniques de l'offre.
    score ∈ [0,1]
    """
    user_skills = [normalize_token(s) for s in profile.skills]
    job_skills = [normalize_token(s) for s in job.get("competences_techniques", []) or []]

    if not user_skills:
        return 0.0

    # on compte combien de skills user apparaissent (exact ou substring) dans job_skills
    match_count = 0
    for us in user_skills:
        for js in job_skills:
            if us in js or js in us:
                match_count += 1
                break

    return match_count / len(user_skills)


# ------------------ 2. Score mode de travail ------------------ #

def compute_mode_travail_score(job: dict, profile: UserProfile) -> float:
    """
    Score ∈ [0,1] basé sur la compatibilité du mode de travail
    (remote / hybride / présentiel).
    """
    preferred_modes = [normalize_token(m) for m in profile.preferred_mode_travail]
    job_mode = normalize_token(job.get("mode_travail") or "")

    if not preferred_modes or not job_mode:
        return 0.0

    if job_mode in preferred_modes:
        return 1.0

    # Cas simple : user veut remote ou hybride, mais job est présentiel
    if job_mode == "presentiel" and ("remote" in preferred_modes or "hybride" in preferred_modes):
        return 0.2  # pas idéal

    # Sinon neutralité
    return 0.5


# ------------------ 3. Score localisation ------------------ #

def compute_location_score(job: dict, profile: UserProfile) -> float:
    """
    Score ∈ [0,1] fondé sur la présence de la ville / pays dans les préférences.
    Matching par substring sur la location (très simple).
    """
    preferred_locations = [normalize_token(c) for c in profile.preferred_locations]
    job_loc = normalize_token(job.get("location") or "")

    if not preferred_locations or not job_loc:
        return 0.0

    for loc in preferred_locations:
        if loc and loc in job_loc:
            return 1.0

    return 0.0


# ------------------ 4. Score rémunération (optionnel, très simple) ------------------ #

def extract_numeric_remuneration(remu_text: str) -> float:
    """
    Tentative très simple pour extraire une valeur numérique principale
    depuis un texte de rémunération.
    Ex: "entre 6000 et 8000 MAD" -> 8000
    """
    if not remu_text:
        return 0.0

    # on récupère tous les nombres
    nums = re.findall(r"\d+(?:[.,]\d+)?", remu_text)
    if not nums:
        return 0.0

    # on prend le max comme approximation
    values = []
    for n in nums:
        n = n.replace(",", ".")
        try:
            values.append(float(n))
        except ValueError:
            continue

    return max(values) if values else 0.0


def compute_remuneration_score(job: dict, profile: UserProfile) -> float:
    """
    Score ∈ [0,1] basé sur la rémunération.
    1 si >= min_remuneration
    0.5 si légèrement en dessous
    0 si très inférieur ou pas d'info.
    """
    if profile.min_remuneration is None:
        return 0.0

    remu_text = job.get("remuneration") or ""
    remu_val = extract_numeric_remuneration(remu_text)
    if remu_val <= 0:
        return 0.0

    min_required = profile.min_remuneration

    if remu_val >= min_required:
        return 1.0
    elif remu_val >= 0.7 * min_required:
        return 0.5
    else:
        return 0.0


# ------------------ 5. Calcul global des scores de règles ------------------ #

def compute_rule_scores_for_job(job: dict, profile: UserProfile) -> dict:
    """
    Calcule tous les sous-scores de règles pour une offre.
    """
    score_skills = compute_skill_score(job, profile)
    score_mode = compute_mode_travail_score(job, profile)
    score_loc = compute_location_score(job, profile)
    score_remu = compute_remuneration_score(job, profile)

    return {
        "score_skills": score_skills,
        "score_mode_travail": score_mode,
        "score_location": score_loc,
        "score_remuneration": score_remu,
    }


# ------------------ 6. Fusion avec score_embedding ------------------ #

def compute_final_score(job: dict, rule_scores: dict) -> Tuple[float, dict]:
    """
    Fusionne score_embedding + scores de règles en un score_final.
    Retourne score_final + détail.
    """

    score_embedding = float(job.get("score_embedding", 0.0))

    score_skills = rule_scores["score_skills"]
    score_mode = rule_scores["score_mode_travail"]
    score_loc = rule_scores["score_location"]
    # score_remu = rule_scores["score_remuneration"]  # dispo si tu veux l'utiliser directement

    # Fusion simple (pondérations ajustables)
    score_final = (
        0.6 * score_embedding +
        0.25 * score_skills +
        0.10 * score_mode +
        0.05 * score_loc
    )

    return score_final, {
        "score_embedding": score_embedding,
        **rule_scores,
        "score_final": score_final,
    }


# ------------------ 7. Pipeline complet : lire fichier, scorer, sauvegarder ------------------ #

def apply_rule_scoring_and_fusion(
    input_path: str = "indeed_stages_data_ia_scored.json",
    output_path: str = "indeed_stages_data_ia_scored_final.json",
    user_profile_path: str = "user_profile.json",
) -> None:
    """
    Lis le fichier d'offres (contenant déjà score_embedding),
    calcule les scores de règles + score_final,
    et écrit un nouveau fichier JSON.
    """
    print(f"📂 Chargement profil depuis {user_profile_path} ...")
    profile = load_user_profile(user_profile_path)

    print(f"📂 Chargement des offres depuis {input_path} ...")
    jobs = load_jobs(input_path)
    print(f"   → {len(jobs)} offres chargées.")

    enriched_jobs: List[dict] = []

    for job in jobs:
        rule_scores = compute_rule_scores_for_job(job, profile)
        score_final, detail = compute_final_score(job, rule_scores)

        job_enriched = {
            **job,
            "score_rules": {
                "score_skills": detail["score_skills"],
                "score_mode_travail": detail["score_mode_travail"],
                "score_location": detail["score_location"],
                "score_remuneration": detail["score_remuneration"],
            },
            "score_embedding": detail["score_embedding"],
            "score_final": detail["score_final"],
        }
        enriched_jobs.append(job_enriched)

    # On trie par score_final décroissant
    enriched_jobs_sorted = sorted(enriched_jobs, key=lambda x: x.get("score_final", 0.0), reverse=True)

    out_path = Path(output_path)
    out_path.write_text(
        json.dumps(enriched_jobs_sorted, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"✅ Fichier avec scores fusionnés écrit : {out_path.resolve()}")


if __name__ == "__main__":
    apply_rule_scoring_and_fusion(
        input_path="app/services/indeed_stages_data_ia_scored.json",
        output_path="app/services/indeed_stages_data_ia_scored_final.json",
        user_profile_path="user_profile.json",
    )
