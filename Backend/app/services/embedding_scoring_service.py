# app/services/embedding_scoring_service.py

import json
from pathlib import Path
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from app.schemas.user_profile import UserProfile


# --------------------------------------------------------
# 1. Chargement du profil utilisateur
# --------------------------------------------------------


def load_user_profile(path: str = "user_profile.json") -> UserProfile:
    """
    Charge le profil utilisateur depuis un fichier JSON
    et le convertit en objet UserProfile (Pydantic).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Fichier profil introuvable : {p.resolve()}")
    data = json.loads(p.read_text(encoding="utf-8"))
    return UserProfile(**data)


def build_user_text(profile: UserProfile) -> str:
    """
    Construit un texte riche à partir du profil utilisateur.
    Ce texte sera encodé en embedding.
    """
    parts: List[str] = []

    parts.append(f"Poste recherché : {profile.target_job}.")

    if profile.skills:
        parts.append("Compétences principales : " + ", ".join(profile.skills) + ".")

    if profile.soft_skills:
        parts.append("Soft skills : " + ", ".join(profile.soft_skills) + ".")

    if profile.preferred_locations:
        parts.append("Lieux / contextes souhaités : " + ", ".join(profile.preferred_locations) + ".")

    if profile.preferred_mode_travail:
        parts.append("Modes de travail préférés : " + ", ".join(profile.preferred_mode_travail) + ".")

    if profile.min_remuneration is not None:
        parts.append(
            f"Rémunération minimale souhaitée : {profile.min_remuneration} {profile.currency} (approx.)."
        )

    return "\n".join(parts)


# --------------------------------------------------------
# 2. Construction du texte pour chaque offre
# --------------------------------------------------------


def build_job_repr_text(job: dict) -> str:
    """
    Construit un texte représentatif d'une offre pour l'embedding.

    On suppose qu'on lit les offres depuis le JSON ENRICHI,
    donc on a potentiellement:
      - title, company, location, description
      - competences_techniques, competences_soft, nice_to_have_skills,
      - missions_principales, mode_travail, remuneration, etc.
    """
    title = job.get("title", "")
    company = job.get("company") or ""
    location = job.get("location") or ""
    description = job.get("description") or ""

    competences_techniques = job.get("competences_techniques", []) or []
    competences_soft = job.get("competences_soft", []) or []
    nice_to_have_skills = job.get("nice_to_have_skills", []) or []
    missions = job.get("missions_principales", []) or []
    mode_travail = job.get("mode_travail") or ""
    remuneration = job.get("remuneration") or ""

    parts: List[str] = []

    parts.append(f"Titre de l'offre : {title}")
    if company:
        parts.append(f"Entreprise : {company}")
    if location:
        parts.append(f"Lieu : {location}")

    if mode_travail:
        parts.append(f"Mode de travail : {mode_travail}")

    if description:
        parts.append("Description brute :")
        parts.append(description)

    if competences_techniques:
        parts.append("Compétences techniques recherchées : " + ", ".join(competences_techniques) + ".")

    if nice_to_have_skills:
        parts.append("Compétences nice to have : " + ", ".join(nice_to_have_skills) + ".")

    if competences_soft:
        parts.append("Soft skills recherchées : " + ", ".join(competences_soft) + ".")

    if missions:
        parts.append("Missions principales : " + " ".join(missions))

    if remuneration:
        parts.append("Rémunération mentionnée : " + remuneration)

    return "\n".join(parts)


# --------------------------------------------------------
# 3. Embeddings + similarités
# --------------------------------------------------------


def compute_cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calcule la similarité cosinus entre deux vecteurs numpy 1D.
    Renvoie une valeur entre -1 et 1.
    """
    if a.ndim > 1:
        a = a.reshape(-1)
    if b.ndim > 1:
        b = b.reshape(-1)

    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def score_jobs_with_embeddings(
    input_path: str = "indeed_stages_data_ia_enriched.json",
    output_path: str = "indeed_stages_data_ia_scored.json",
    user_profile_path: str = "user_profile.json",
) -> None:
    """
    Charge le profil utilisateur + les offres enrichies,
    calcule un score de similarité embedding pour chaque offre,
    et écrit un nouveau JSON avec un champ `score_embedding`.
    """

    in_path = Path(input_path)
    if not in_path.exists():
        raise FileNotFoundError(f"Fichier d'offres introuvable : {in_path.resolve()}")

    print(f"📂 Chargement des offres depuis {in_path} ...")
    jobs: List[dict] = json.loads(in_path.read_text(encoding="utf-8"))
    print(f"   → {len(jobs)} offres chargées.")

    # 1) Profil utilisateur
    print(f"📂 Chargement du profil utilisateur : {user_profile_path} ...")
    profile = load_user_profile(user_profile_path)
    user_text = build_user_text(profile)

    # 2) Préparation des textes d'offres
    print("📝 Construction des textes représentatifs des offres ...")
    job_texts = [build_job_repr_text(job) for job in jobs]

    # 3) Chargement du modèle d'embedding
    print("🧠 Chargement du modèle d'embedding (sentence-transformers) ...")
    # Modèle multilingue adapté au FR
    model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    model = SentenceTransformer(model_name)

    # 4) Embeddings
    print("⚙️ Encodage du profil utilisateur ...")
    user_emb = model.encode(user_text, convert_to_numpy=True)

    print("⚙️ Encodage des offres (batch) ...")
    job_embs = model.encode(
        job_texts,
        convert_to_numpy=True,
        batch_size=16,
        show_progress_bar=True,
    )

    # 5) Similarités
    print("📊 Calcul des similarités cosinus ...")
    scores: List[float] = []
    for emb in job_embs:
        sim = compute_cosine_similarity(user_emb, emb)  # ∈ [-1, 1]
        # Remap en [0,1] pour que ce soit plus lisible
        score_01 = (sim + 1.0) / 2.0
        scores.append(score_01)

    # 6) Ajout du score aux offres
    print("🧩 Ajout du champ 'score_embedding' aux offres ...")
    for job, score in zip(jobs, scores):
        job["score_embedding"] = score

    # 7) Tri optionnel des offres par score décroissant
    jobs_sorted = sorted(jobs, key=lambda x: x.get("score_embedding", 0.0), reverse=True)

    # 8) Sauvegarde
    out_path = Path(output_path)
    out_path.write_text(
        json.dumps(jobs_sorted, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"✅ Fichier avec scores embedding écrit : {out_path.resolve()}")


if __name__ == "__main__":
    # Script simple : score toutes les offres d'indeed_stages_data_ia_enriched.json
    score_jobs_with_embeddings(
        input_path="indeed_stages_data_ia_enriched.json",
        output_path="indeed_stages_data_ia_scored.json",
        user_profile_path="user_profile.json",
    )
