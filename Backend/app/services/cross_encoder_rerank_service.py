# app/services/cross_encoder_rerank_service.py

import json
import math
from pathlib import Path
from typing import List, Tuple

from sentence_transformers import CrossEncoder

from app.services.embedding_scoring_service import (
    load_user_profile,
    build_user_text,
    build_job_repr_text,
)


def sigmoid(x: float) -> float:
    """
    Transforme un score non borné (logit) en valeur entre 0 et 1.
    Interprétation : compatibilité estimée.
    """
    return 1.0 / (1.0 + math.exp(-x))


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
    Pipeline :
    1) Chargement des offres scorées (embeddings + règles)
    2) Sélection Top-K
    3) Cross-encoder sur Top-K
    4) Reranking fin
    5) Ajout score_match ∈ [0,1] via sigmoid
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

    # 2) Tri par score_final (embeddings + règles)
    print("📊 Tri préalable des offres par score_final ...")
    jobs_sorted = sorted(
        jobs,
        key=lambda x: float(x.get("score_final", 0.0)),
        reverse=True,
    )

    # 3) Sélection Top-K
    top_k = min(top_k, len(jobs_sorted))
    top_jobs = jobs_sorted[:top_k]
    rest_jobs = jobs_sorted[top_k:]

    print(f"🔍 Reranking cross-encoder sur les {top_k} meilleures offres ...")

    # 4) Construction des paires
    pairs = build_pairs_for_cross_encoder(top_jobs, user_text)

    # 5) Chargement du modèle cross-encoder
    model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    print(f"🧠 Chargement du cross-encoder : {model_name} ...")
    cross_encoder = CrossEncoder(model_name)

    # 6) Prédiction
    print("⚙️ Prédiction des scores cross-encoder ...")
    ce_scores = cross_encoder.predict(pairs)

    # 7) Ajout des scores
    for job, ce_score in zip(top_jobs, ce_scores):
        ce_score = float(ce_score)
        job["score_cross_encoder"] = ce_score
        job["score_match"] = sigmoid(ce_score)  # ✅ score entre 0 et 1

    # 8) Reranking final (sur score brut, pas la sigmoid)
    top_jobs_reranked = sorted(
        top_jobs,
        key=lambda x: float(x.get("score_cross_encoder", 0.0)),
        reverse=True,
    )

    # 9) Concaténation
    final_jobs = top_jobs_reranked + rest_jobs

    # 10) Sauvegarde
    out_path = Path(output_path)
    out_path.write_text(
        json.dumps(final_jobs, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"✅ Fichier reranké écrit : {out_path.resolve()}")


if __name__ == "__main__":
    rerank_with_cross_encoder(
        input_path="app/services/indeed_stages_data_ia_scored_final.json",
        output_path="app/services/indeed_stages_data_ia_reranked.json",
        user_profile_path="user_profile.json",
        top_k=15,
    )