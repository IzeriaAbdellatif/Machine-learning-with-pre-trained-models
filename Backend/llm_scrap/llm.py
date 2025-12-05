from groq import Groq
from dotenv import load_dotenv
import os
import pandas as pd
import time
import json

# -----------------------------
# 1) Charger la clé API Groq
# -----------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")


client = Groq(api_key=api_key)

# -----------------------------
# 2) Prompts LLM
# -----------------------------

SYSTEM_PROMPT = """
Tu es un assistant qui structure des offres d'emploi techniques (Data, IA, Software, etc.).
À partir des infos brutes (titre, description, entreprise, lieu, URL),
tu dois renvoyer STRICTEMENT un objet JSON avec les champs suivants :

{
  "title": "...",
  "company": "...",
  "location": "...",
  "job_url": "...",
  "job_category": "...",
  "seniority": "...",
  "required_skills": ["...", "..."],
  "nice_to_have_skills": ["...", "..."],
  "remote_type": "onsite | remote | hybrid | unknown",
  "contract_type": "CDI | CDD | Stage | Freelance | Autre | unknown"
}

Règles importantes :
- Les listes doivent être de VRAIES listes JSON (["...", "..."]).
- Si une information n'est pas claire, mets "unknown".
- Ne renvoie QUE du JSON. Pas de texte autour.
"""

USER_TEMPLATE = """
Titre du poste : {title}

Entreprise : {company}
Lieu : {location}

Description :
{description}

URL de l'offre :
{job_url}

Analyse cette offre et renvoie STRICTEMENT le JSON demandé.
"""


# -----------------------------
# 3) Chemins des fichiers
# -----------------------------

INPUT_PATH = "offres_scrap.json"        # fichier brut (scraping Indeed)
OUTPUT_PATH = "offres_structured.json"  # fichier structuré par le LLM
MAX_JOBS = None    # ou par ex. 50 si tu veux limiter pour les tests


# -----------------------------
# 4) Fonction : structurer une offre
# -----------------------------

def structure_one_job(row: dict) -> dict:
    """
    Prend une ligne d'offre Indeed (dict) et retourne un dict structuré (JSON).
    Version simple : pas de try/except.
    """

    title = row.get("title", "") or ""
    description = row.get("description", "") or ""
    company = row.get("company", "") or ""
    location = row.get("location", "") or ""
    job_url = row.get("job_url", "") or ""

    # On construit le message utilisateur à partir du template
    user_msg = USER_TEMPLATE.format(
        title=title,
        description=description,
        company=company,
        location=location,
        job_url=job_url
    )

    # Appel à Groq Llama 3
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )

    content = resp.choices[0].message.content.strip()
    # On suppose que le modèle renvoie du JSON valide
    data = json.loads(content)
    return data


# -----------------------------
# 5) Main : boucle sur toutes les offres
# -----------------------------

def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Fichier introuvable : {INPUT_PATH}")

    print(f"Chargement des offres depuis {INPUT_PATH}")
    jobs_df = pd.read_json(INPUT_PATH)

    if MAX_JOBS is not None and len(jobs_df) > MAX_JOBS:
        jobs_df = jobs_df.head(MAX_JOBS).copy()
        print(f"⚠️ On ne garde que les {MAX_JOBS} premières offres pour le test.")

    structured_rows = []
    t0 = time.time()

    for i, (_, row) in enumerate(jobs_df.iterrows(), start=1):
        print(f"\n🧩 Traitement offre {i}/{len(jobs_df)} (job_id={row.get('job_id')})")

        row_dict = row.to_dict()
        data_struct = structure_one_job(row_dict)

        if data_struct is not None:
            # On garde l'ID original si présent
            if "job_id" in row_dict:
                data_struct["job_id"] = row_dict["job_id"]
            structured_rows.append(data_struct)

    elapsed = time.time() - t0
    print(f"\n✅ Structuration terminée en {elapsed:.1f} sec")
    print(f"Nombre d'offres structurées : {len(structured_rows)}")

    # Sauvegarde JSON
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(structured_rows, f, ensure_ascii=False, indent=2)

    print(f" Fichier sauvegardé dans : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
