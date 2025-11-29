import os
import json
import time
from random import uniform

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
import google.generativeai as genai

# =========================
# 1) CONFIG GEMINI
# =========================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY manquant dans le fichier .env")

genai.configure(api_key=API_KEY)

# On utilise un modèle rapide et gratuit
GEMINI_MODEL_NAME = "gemini-1.5-flash"


# =========================
# 2) NETTOYAGE DU TEXTE JSON
# =========================

def clean_json_text(text: str) -> str:
    """
    Le modèle renvoie parfois du texte autour ou des ```json.
    On garde juste ce qui est entre le premier '{' et le dernier '}'.
    """
    text = text.strip()

    # enlever les ```json ou ``` éventuels
    if text.startswith("```"):
        # supprime tous les ` au début/fin
        text = text.strip("`")
        # si "{" existe, on coupe avant
        if "{" in text:
            text = text[text.index("{"):]

    # garder juste l'objet JSON
    if "{" in text and "}" in text:
        start = text.index("{")
        end = text.rindex("}") + 1
        text = text[start:end]

    return text


# =========================
# 3) APPEL GEMINI
# =========================

def call_llm(prompt: str) -> dict:
    """
    Appelle le modèle Gemini et renvoie un dict Python (JSON parsé).
    Lève une exception si JSON invalide.
    """
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.1,
            "max_output_tokens": 350,
        },
    )

    # Gemini renvoie généralement la réponse dans response.text
    content = response.text
    content = clean_json_text(content)

    data = json.loads(content)  # peut lever JSONDecodeError
    return data


# =========================
# 4) CONSTRUCTION DU PROMPT
# =========================

def build_prompt(row) -> str:
    """
    Construit un prompt en français pour structurer une offre d'emploi.
    On utilise les colonnes brutes de ton fichier JSON/CSV.
    """

    description = row.get("description", row.get("Description", "")) or ""
    # on tronque pour ne pas exploser le nombre de tokens
    description = description[:1500]

    prompt = f"""
Tu es un assistant spécialisé en analyse d'offres d'emploi en Data/IA au Maroc.

Ton objectif est de transformer l'offre suivante en JSON STRICTEMENT valide
avec exactement cette structure (champs obligatoires) :

{{
  "job_title": "",
  "company_name": "",
  "city": "",
  "country": "",
  "is_remote": false,
  "work_mode": "Remote | Présentiel | Hybride | Inconnu",
  "contract_type": "CDI | CDD | Stage | Freelance | Alternance | Autre | Inconnu",
  "job_level": "Junior | Intermédiaire | Senior | Manager | Inconnu",
  "job_domain": "Data Scientist | Data Analyst | Data Engineer | Machine Learning Engineer | AI Engineer | Autre",
  "required_skills": [],
  "languages": [],
  "salary_min": null,
  "salary_max": null,
  "salary_currency": "MAD | EUR | USD | Autre | Inconnu",
  "description_short": ""
}}

Règles importantes :
- Si une information n'est pas explicite, mets "Inconnu" ou null pour les nombres.
- "city" doit être une ville (Casablanca, Rabat, Fès...). Si tu ne sais pas : "Inconnu".
- "country" = "Maroc" en général.
- "is_remote" = true seulement si le télétravail/remote est clairement mentionné.
- "work_mode" = "Remote" si 100% télétravail, "Hybride" si mixte, sinon "Présentiel" ou "Inconnu".
- "job_domain" = choisis la catégorie la plus pertinente parmi celles proposées.
- "required_skills" = liste de compétences techniques ou analytiques importantes (Python, SQL, ML, Power BI, etc.).
- "languages" = liste des langues exigées (ex : "Français", "Anglais").
- "description_short" = un résumé très court (1-2 phrases) de l'offre.
- Réponds UNIQUEMENT avec l'objet JSON, sans texte autour, sans ```.

Voici les données brutes de l'offre :

Mot-clé de recherche : {row.get('search_keyword', '')}
Titre brut : {row.get('title', row.get('Title', ''))}
Entreprise brute : {row.get('company', row.get('Company', ''))}
Lieu brut : {row.get('location', row.get('Location', ''))}
Meta brute : {row.get('meta', row.get('Meta', ''))}
Date d'extraction : {row.get('extract_date', '')}

Description complète (tronquée si trop longue) :
\"\"\" 
{description}
\"\"\" 
"""
    return prompt


# =========================
# 5) CHARGEMENT DU FICHIER BRUT
# =========================

def load_offers(input_path: str) -> pd.DataFrame:
    """
    Charge les offres à partir d'un fichier JSON ou CSV.
    - .json : suppose une liste de dicts
    - .csv : charge via pandas.read_csv
    """
    if input_path.lower().endswith(".json"):
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    elif input_path.lower().endswith(".csv"):
        df = pd.read_csv(input_path)
    else:
        raise ValueError("Format de fichier non supporté (utilise .json ou .csv).")

    return df


# =========================
# 6) PIPELINE : BRUT → STRUCTURÉ
# =========================

def enrich_offers_with_llm(input_path: str, output_csv: str, max_rows=None):
    df = load_offers(input_path)

    if max_rows is not None:
        df = df.head(max_rows)

    print(f"[INFO] Nombre d'offres à traiter : {len(df)}")

    structured_rows = []
    nb_ok = 0

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        print(f"\n[INFO] Offre {idx + 1}/{len(df)}")

        prompt = build_prompt(row)

        try:
            data = call_llm(prompt)
        except Exception as e:
            print(f"[ERREUR] Problème avec Gemini sur la ligne {idx} : {e}")
            continue

        # On garde quelques infos brutes pour le lien avec le dataset initial
        data["source_search_keyword"] = row.get("search_keyword", "")
        data["source_title_raw"] = row.get("title", row.get("Title", ""))
        data["source_company_raw"] = row.get("company", row.get("Company", ""))
        data["source_location_raw"] = row.get("location", row.get("Location", ""))
        data["source_extract_date"] = row.get("extract_date", "")
        data["original_index"] = int(idx)

        structured_rows.append(data)
        nb_ok += 1

        # petite pause pour éviter de spammer l'API
        time.sleep(uniform(0.2, 0.5))

    if structured_rows:
        df_struct = pd.DataFrame(structured_rows)
        df_struct.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"\n[OK] Fichier structuré sauvegardé : {output_csv}")
        print(f"[INFO] Offres traitées avec succès : {nb_ok}/{len(df)}")
    else:
        print("\n[WARN] Aucun résultat structuré généré.")


# =========================
# 7) MAIN
# =========================

if __name__ == "__main__":
    enrich_offers_with_llm(
        input_path="indeed_stages_data_ia.json",   # ton fichier brut (JSON ou CSV)
        output_csv="offers_structured_gemini.csv", # sortie structurée
        max_rows=None,                             # ex: 20 pour test, None pour tout
    )
