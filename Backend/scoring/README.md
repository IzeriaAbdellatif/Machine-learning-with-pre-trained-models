# Job Matching & Scoring System 

Ce projet consiste à développer un système intelligent qui **score automatiquement les offres d’emploi scrappées depuis Indeed**, en fonction d’un **profil utilisateur** (compétences, expérience, formation, localisation…).

Le système utilise :
- le **NLP** (embeddings sémantiques),
- la **similarité cosine**,
- des **critères métier** (compétences, ville, remote, type de contrat),

---

#  1. Données utilisées

Le projet exploite **exclusivement les données scrappées depuis Indeed**, ainsi que le profil utilisateur.

## 1️⃣ `jobs_scraped.csv`
Contient les informations extraites d’Indeed :

| Colonne            | Description                                  |
|--------------------|----------------------------------------------|
| `job_id`           | ID unique généré                              |
| `title`            | Titre du poste                                |
| `company`          | Entreprise                                     |
| `location`         | Ville / région                                 |
| `description`      | Description du poste                           |
| `requirements`     | Compétences / conditions demandées             |
| `work_mode`        | Remote / Présentiel                            |
| `contract_type`    | CDI / CDD / Stage                              |
| `date_posted`      | Date de publication                            |

Un texte unifié est créé pour le NLP :

```python
jobs["job_text"] = (
    jobs["title"].fillna("") + " " +
    jobs["description"].fillna("") + " " +
    jobs["requirements"].fillna("")
)
