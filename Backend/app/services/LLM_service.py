# app/services/LLM_service.py

from groq import Groq
from app.core.config import settings

# Réponse "vide" par défaut si le LLM plante
DEFAULT_EMPTY_JSON = """{
  "type_poste": "non_precise",
  "mode_travail": "non_precise",
  "competences_techniques": [],
  "competences_soft": [],
  "missions_principales": []
}"""


# Client Groq global
client = Groq(api_key=settings.GROQ_API_KEY)


def call_llm(prompt: str) -> str:
    """
    Appelle le modèle Groq de façon SYNCHRONE.
    Si ça échoue (erreur réseau, limite, etc.), on renvoie un JSON vide.
    """
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )

        # contenu texte de la première réponse
        content = response.choices[0].message.content
        if content is None:
            return DEFAULT_EMPTY_JSON
        return content

    except Exception as e:
        print("[ERROR] Erreur lors de l'appel à Groq :", e)
        # On ne bloque pas le pipeline, on renvoie une structure vide
        return DEFAULT_EMPTY_JSON
