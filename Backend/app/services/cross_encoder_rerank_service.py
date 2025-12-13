# app/services/cross_encoder_rerank_service.py

import json
from pathlib import Path
from typing import List, Tuple

from sentence_transformers import CrossEncoder

from app.services.embedding_scoring_service import (
    load_user_profile,
    build_user_text,
    build_job_repr_text,
)


def load_jobs(path: str) -> List[dict]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Fichier d'offres introuvable : {p.resolve()}")
    return json.loads(p.read_text(encoding="utf-8"))


def build_pairs_for_cross_encoder(
    jobs: List[dict],
    user_text: str,
) -> List[Tuple[str, str]]:
    """
    Construit les paires (profil, offre) pour le cross-encoder.
    Chaque élément est un tuple (texte_profil, texte_offre).
    """
    pairs: List[Tuple[str, str]] = []
    for job in jobs:
        job_text = build_job_repr_text(job)
        pairs.append((user_text, job_text))
    return pairs


def rerank_with_cross_encoder(
    input_path: str = "indeed_stages_data_ia_scored_final.json",
    output_path: str = "indeed_stages_data_ia_reranked.json",
    user_profile_path: str = "user_profile.json",
    top_k: int = 30,
) -> None:
    """
    1) Charge les offres avec score_final.
    2) Sélectionne les top_k meilleures offres.
    3) Applique un cross-encoder sur (profil, offre) pour ces top_k.
    4) Rerank ces top_k selon le score cross-encoder.
    5) Concatène :
        - top_k rerankées
        - le reste des offres (dans l'ordre initial par score_final)
    6) Sauvegarde le tout dans output_path.
    """

    in_path = Path(input_path)
    if not in_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {in_path.resolve()}")

    print(f"📂 Chargement des offres depuis {in_path} ...")
    jobs = load_jobs(input_path)
    print(f"   → {len(jobs)} offres chargées.")

    # 1) Profil utilisateur
    print(f"📂 Chargement du profil utilisateur : {user_profile_path} ...")
    profile = load_user_profile(user_profile_path)
    user_text = build_user_text(profile)

    # 2) Tri préalable par score_final (si ce n'est pas déjà le cas)
    print("📊 Tri préalable des offres par score_final ...")
    jobs_sorted = sorted(
        jobs,
        key=lambda x: float(x.get("score_final", 0.0)),
        reverse=True,
    )

    # 3) Sélection des top_k pour reranking
    top_k = min(top_k, len(jobs_sorted))
    top_jobs = jobs_sorted[:top_k]
    rest_jobs = jobs_sorted[top_k:]

    print(f"🔍 Reranking cross-encoder sur les {top_k} meilleures offres ...")

    # 4) Construction des paires (profil, offre)
    pairs = build_pairs_for_cross_encoder(top_jobs, user_text)

    # 5) Chargement du modèle cross-encoder
    # Modèle très utilisé pour le reranking (anglais), marche aussi raisonnablement pour du FR.
    model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    print(f"🧠 Chargement du cross-encoder : {model_name} ...")
    cross_encoder = CrossEncoder(model_name)

    # 6) Prédiction des scores
    print("⚙️ Prédiction des scores cross-encoder ...")
    ce_scores = cross_encoder.predict(pairs)  # array de floats

    # 7) Ajout des scores cross-encoder aux top_jobs
    for job, ce_score in zip(top_jobs, ce_scores):
        job["score_cross_encoder"] = float(ce_score)

    # 8) Reranking des top_jobs selon score_cross_encoder décroissant
    top_jobs_reranked = sorted(
        top_jobs,
        key=lambda x: float(x.get("score_cross_encoder", 0.0)),
        reverse=True,
    )

    # 9) Concat : top_jobs rerankées + reste des offres (non modifiées)
    final_jobs = top_jobs_reranked + rest_jobs

    # 10) Sauvegarde
    out_path = Path(output_path)
    out_path.write_text(
        json.dumps(final_jobs, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"✅ Fichier reranké (cross-encoder) écrit : {out_path.resolve()}")


if __name__ == "__main__":
    rerank_with_cross_encoder(
        input_path="app/services/indeed_stages_data_ia_scored_final.json",
        output_path="app/services/indeed_stages_data_ia_reranked.json",
        user_profile_path="user_profile.json",
        top_k=15,  # tu peux ajuster
    )
