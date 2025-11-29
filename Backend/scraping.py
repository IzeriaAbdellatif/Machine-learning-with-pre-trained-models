import time
import json
from datetime import datetime
from urllib.parse import quote_plus

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================
# 1) URL de recherche AVEC pagination
# =========================
def build_search_url(keyword: str, location: str, start: int = 0) -> str:
    """
    Construit l'URL de recherche Indeed pour un mot-clé et une localisation.
    - start : index de départ pour la pagination (0, 10, 20, ...)
    """
    base_url = "https://ma.indeed.com/jobs"
    q = quote_plus(keyword)
    loc = quote_plus(location)
    url = f"{base_url}?q={q}&l={loc}"
    if start > 0:
        url += f"&start={start}"
    return url


# =========================
# 2) FONCTION PRINCIPALE DE SCRAPING
#    (AVEC PAGINATION + LOGIN MANUEL + MAX PAGES)
# =========================
def scrape_indeed_offers(
    keywords: list[str],
    location: str,
    output_json: str,
    max_offers_per_kw: int | None = None,
    max_pages: int = 5,   # <<== NOUVEAU : max 5 pages par mot-clé
):
    """
    Scrape les offres Indeed pour plusieurs mots-clés liés aux stages et à la Data/IA.
    - keywords : liste de requêtes (ex: ["stage data", "data scientist", ...])
    - location : ex. "Maroc"
    - max_offers_per_kw : limite optionnelle du nombre d'offres par mot-clé
                          (toutes pages confondues). None = pas de limite.
    - max_pages : nombre maximum de pages à traiter par mot-clé
    """

    options = uc.ChromeOptions()
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    driver = None
    all_offers = []

    ul_selector = "ul.css-pygyny.eu4oa1w0"
    li_selector = "li.css-1ac2h1w.eu4oa1w0"

    try:
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 15)

        # ============================
        # 2.0. Connexion manuelle à Indeed
        # ============================
        print("\n================ CONNEXION MANUELLE =================")
        driver.get("https://ma.indeed.com/")
        print("[ACTION] Dans la fenêtre Chrome :")
        print("  1) Clique sur 'Connexion' / 'Se connecter'")
        print("  2) Connecte-toi avec ton compte Google")
        print("  3) Quand tu es bien connecté, appuie sur ENTRÉE ici.")
        input(">>> Appuie sur ENTRÉE quand la connexion est terminée... ")
        print("=====================================================\n")

        # ============================
        # 2.1. Boucle sur les mots-clés
        # ============================
        for kw in keywords:
            print("\n" + "=" * 70)
            print(f"[INFO] Mot-clé de recherche : {kw}")

            offers_for_kw = 0   # compteur d'offres pour ce mot-clé
            start = 0           # index de pagination (0, 10, 20, ...)
            page_num = 1        # <<== numéro de page (1, 2, 3, ...)

            while True:
                print("\n" + "-" * 60)
                print(f"[INFO] Page {page_num}/{max_pages} pour '{kw}', start={start}")

                # Stop si on a déjà traité max_pages
                if page_num > max_pages:
                    print(f"[INFO] Nombre max de pages ({max_pages}) atteint pour '{kw}'.")
                    break

                url = build_search_url(kw, location, start=start)
                print(f"[INFO] Ouverture de l'URL : {url}")
                driver.get(url)
                time.sleep(5)

                # Récupérer le <ul> principal
                try:
                    ul_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ul_selector))
                    )
                except Exception:
                    print("[WARN] Impossible de trouver le conteneur <ul> des offres. On arrête la pagination pour ce mot-clé.")
                    break

                offer_elements = ul_element.find_elements(By.CSS_SELECTOR, li_selector)
                nb_offres_page = len(offer_elements)
                print(f"[INFO] Nombre d'offres trouvées sur cette page : {nb_offres_page}")

                # Si aucune offre sur cette page → fin de la pagination
                if nb_offres_page == 0:
                    print("[INFO] Aucune offre sur cette page, fin de la pagination pour ce mot-clé.")
                    break

                # Gestion du max_offers_per_kw
                if max_offers_per_kw is not None:
                    remaining = max_offers_per_kw - offers_for_kw
                    if remaining <= 0:
                        print("[INFO] Limite max_offers_per_kw atteinte pour ce mot-clé.")
                        break
                    nb_to_process = min(nb_offres_page, remaining)
                else:
                    nb_to_process = nb_offres_page

                # ============================
                #   BOUCLE SUR LES OFFRES DE LA PAGE
                # ============================
                for i in range(nb_to_process):
                    print(f"\n[INFO] Traitement offre {i+1}/{nb_to_process} sur la page, mot-clé '{kw}'")

                    # Re-sélectionner les éléments pour éviter les stale elements
                    try:
                        ul_element = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ul_selector))
                        )
                        offer_elements = ul_element.find_elements(By.CSS_SELECTOR, li_selector)
                    except Exception:
                        print("[WARN] Impossible de recharger la liste des offres.")
                        break

                    if i >= len(offer_elements):
                        print("[WARN] Moins d'offres que prévu, on arrête sur cette page.")
                        break

                    offer_li = offer_elements[i]

                    # Scroll + clic sur l'offre
                    try:
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", offer_li
                        )
                        time.sleep(1)

                        # on essaye un clic "classique"
                        try:
                            offer_li.click()
                        except Exception:
                            # fallback : clic JS
                            driver.execute_script("arguments[0].click();", offer_li)

                    except Exception as e:
                        print(f"[WARN] Impossible de cliquer sur l'offre {i+1} : {e}")
                        continue

                    # Attendre la right pane
                    try:
                        wait.until(
                            EC.presence_of_element_located(
                                (
                                    By.CSS_SELECTOR,
                                    "div.jobsearch-RightPane.css-6iabie.eu4oa1w0",
                                )
                            )
                        )
                    except Exception:
                        print("[WARN] Right pane non trouvée, on passe à l'offre suivante.")
                        continue

                    time.sleep(2)

                    # ==============================
                    #   Extraction des informations
                    # ==============================

                    # Title
                    try:
                        title = driver.find_element(
                            By.CSS_SELECTOR,
                            "div.jobsearch-JobInfoHeader-title-container",
                        ).text
                    except Exception:
                        title = ""

                    # Company
                    try:
                        company = driver.find_element(
                            By.CSS_SELECTOR,
                            "span.css-qcqa6h.e1wnkr790",
                        ).text
                    except Exception:
                        company = ""

                    # Location
                    try:
                        location_text = driver.find_element(
                            By.CSS_SELECTOR,
                            "div#jobLocationText",
                        ).text
                    except Exception:
                        location_text = ""

                    # Meta (type contrat, date, etc.)
                    try:
                        meta = driver.find_element(
                            By.CSS_SELECTOR,
                            "div.jobsearch-JobMetadataFooter",
                        ).text
                    except Exception:
                        meta = ""

                    # Description
                    try:
                        description = driver.find_element(
                            By.CSS_SELECTOR,
                            "div#jobDescriptionText",
                        ).text
                    except Exception:
                        description = ""

                    # ===== Détection remote / présentiel =====
                    try:
                        loc_lower = location_text.lower()
                        remote_keywords = [
                            "remote",
                            "télétravail",
                            "teletravail",
                            "work from home",
                            "full remote",
                            "fully remote",
                        ]

                        if any(k in loc_lower for k in remote_keywords):
                            is_remote = 1
                            work_mode = "Remote"
                        elif location_text.strip():
                            is_remote = 0
                            work_mode = "Présentiel"
                        else:
                            is_remote = None
                            work_mode = "Inconnu"
                    except Exception:
                        is_remote = None
                        work_mode = "Inconnu"

                    offer_data = {
                        "search_keyword": kw,
                        "title": title,
                        "company": company,
                        "location": location_text,
                        "meta": meta,
                        "description": description,
                        "extract_date": datetime.now().strftime("%Y-%m-%d"),
                        "work_mode": work_mode,
                        "is_remote": is_remote,
                    }

                    all_offers.append(offer_data)
                    offers_for_kw += 1
                    print(f"[INFO] Offre extraite pour '{kw}'. Total pour ce mot-clé : {offers_for_kw}")

                    # Si on atteint max_offers_per_kw en plein milieu de la page, on arrête tout de suite
                    if max_offers_per_kw is not None and offers_for_kw >= max_offers_per_kw:
                        print("[INFO] Limite max_offers_per_kw atteinte pendant la page.")
                        break

                # Fin boucle sur les offres de la page

                # Vérifier encore la limite d'offres
                if max_offers_per_kw is not None and offers_for_kw >= max_offers_per_kw:
                    break

                # Aller à la page suivante
                start += 10
                page_num += 1   # <<== on incrémente le numéro de page

            # fin while pagination pour ce mot-clé

        # Sauvegarde JSON globale
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(all_offers, f, ensure_ascii=False, indent=2)

        print("\n[SUCCESS] JSON sauvegardé :", output_json)
        print(f"[INFO] Nombre total d'offres enregistrées : {len(all_offers)}")

    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass


# =========================
# 3) MAIN
# =========================
if __name__ == "__main__":
    keywords = [
        "stage data",
        "stage data science",
        "stage intelligence artificielle",
        "data scientist",
        "data analyst",
        "machine learning engineer",
        "AI engineer",
    ]

    scrape_indeed_offers(
        keywords=keywords,
        location="Maroc",
        output_json="indeed_stages_data_ia.json",
        max_offers_per_kw=None,  # limite sur nb d'offres (None = pas de limite)
        max_pages=5,             # <<== ICI : 5 pages max par mot-clé
    )
