import time
import json
from datetime import datetime
from urllib.parse import quote_plus
from random import uniform

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================
#  UTILITAIRES
# =========================

def human_sleep(min_s: float = 2.0, max_s: float = 5.0):
    """Pause aléatoire pour rendre le scraping plus humain."""
    time.sleep(uniform(min_s, max_s))


def build_search_url(keyword: str, location: str, start: int = 0) -> str:
    """
    Construit l'URL de recherche Indeed avec pagination.
    'start' est le décalage (0 pour page 1, 10 pour page 2, etc.)
    """
    base_url = "https://ma.indeed.com/jobs"
    q = quote_plus(keyword)
    loc = quote_plus(location)
    return f"{base_url}?q={q}&l={loc}&start={start}"


# =========================
#  FONCTION PRINCIPALE
# =========================

def scrape_indeed_offers(
    keywords: list[str],
    location: str,
    output_json: str,
    max_offers_per_kw: int | None = None,
    max_pages_per_kw: int | None = 5,
):
    """
    Scrape les offres Indeed pour plusieurs mots-clés liés aux stages et à la Data/IA.

    - keywords : liste de requêtes (ex: ["stage data", "data scientist", ...])
    - location : ex. "Maroc"
    - max_offers_per_kw : nombre max d'offres à collecter par mot-clé (sur toutes les pages)
    - max_pages_per_kw : nombre max de pages à visiter par mot-clé
    """

    options = uc.ChromeOptions()
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    driver = None
    all_offers = []

    try:
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 15)

        ul_selector = "ul.css-pygyny.eu4oa1w0"
        li_selector = "li.css-1ac2h1w.eu4oa1w0"

        # =========================
        #  OPTION A : LOGIN MANUEL
        # =========================
        # On ouvre une première page, tu te connectes à Indeed à la main,
        # puis tu appuies sur Entrée dans le terminal.
        print("[INFO] Ouverture initiale pour connexion manuelle à Indeed...")
        driver.get("https://ma.indeed.com/")
        human_sleep(5, 8)
        input("[ACTION] Connecte-toi à Indeed dans la fenêtre, puis appuie sur Entrée ici pour commencer le scraping...")

        for kw in keywords:
            print("\n" + "=" * 60)
            print(f"[INFO] Mot-clé de recherche : {kw}")

            offers_for_kw = 0  # compteur d'offres collectées pour ce mot-clé
            page = 0

            while True:
                if max_pages_per_kw is not None and page >= max_pages_per_kw:
                    print(f"[INFO] max_pages_per_kw={max_pages_per_kw} atteint pour '{kw}'.")
                    break

                # Si limite d'offres atteinte pour ce mot-clé, on arrête
                if max_offers_per_kw is not None and offers_for_kw >= max_offers_per_kw:
                    print(f"[INFO] max_offers_per_kw={max_offers_per_kw} atteint pour '{kw}'.")
                    break

                start_param = page * 10  # Indeed liste 10 offres par page en général
                url = build_search_url(kw, location, start=start_param)
                print(f"[INFO] Ouverture de la page {page+1} pour '{kw}' : {url}")
                driver.get(url)
                human_sleep(4, 7)

                # Scroll léger pour simuler un utilisateur
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
                human_sleep(1, 2)

                # Récupérer le <ul> principal
                try:
                    ul_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ul_selector))
                    )
                except Exception:
                    print("[WARN] Impossible de trouver le conteneur <ul> des offres sur cette page.")
                    break

                offer_elements = ul_element.find_elements(By.CSS_SELECTOR, li_selector)
                print(f"[INFO] Nombre d'offres trouvées sur la page {page+1} pour '{kw}' : {len(offer_elements)}")

                if not offer_elements:
                    print("[INFO] Aucune offre sur cette page, on arrête pour ce mot-clé.")
                    break

                # Boucle sur les offres de cette page
                for i in range(len(offer_elements)):
                    # Vérifier la limite d'offres
                    if max_offers_per_kw is not None and offers_for_kw >= max_offers_per_kw:
                        print(f"[INFO] Limite d'offres atteinte pour '{kw}'.")
                        break

                    print(f"\n[INFO] Traitement offre {i+1}/{len(offer_elements)} sur la page {page+1} pour '{kw}'")

                    # Re-sélectionner les éléments pour éviter stale elements
                    try:
                        ul_element = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ul_selector))
                        )
                        offer_elements = ul_element.find_elements(By.CSS_SELECTOR, li_selector)
                    except Exception:
                        print("[WARN] Impossible de recharger la liste des offres.")
                        break

                    if i >= len(offer_elements):
                        print("[WARN] Moins d'offres que prévu, on arrête cette page.")
                        break

                    offer_li = offer_elements[i]

                    # Récupérer l'URL de l'offre (job_url) depuis le <a> interne
                    job_url = ""
                    try:
                        link_el_for_url = offer_li.find_element(By.CSS_SELECTOR, "a")
                        job_url = link_el_for_url.get_attribute("href") or ""
                    except Exception:
                        pass

                    # Scroll sur l'offre
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", offer_li
                    )
                    human_sleep(0.8, 1.5)

                    # Clic sur le <a> interne plutôt que sur <li> pour éviter element not interactable
                    try:
                        link_el = offer_li.find_element(By.CSS_SELECTOR, "a")
                        driver.execute_script("arguments[0].click();", link_el)
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

                    human_sleep(1.5, 3.0)

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

                    # Description
                    try:
                        description = driver.find_element(
                            By.CSS_SELECTOR,
                            "div#jobDescriptionText",
                        ).text
                    except Exception:
                        description = ""

                    # Lien de postulation (apply_url) - best effort
                    apply_url = ""
                    for css in [
                        "button[aria-label*='Continuer pour postuler']",
                        "a[aria-label*='Continuer pour postuler']",
                        "a[href*='applystart']",
                    ]:
                        try:
                            el = driver.find_element(By.CSS_SELECTOR, css)
                            href = el.get_attribute("href")
                            if href:
                                apply_url = href
                                break
                        except Exception:
                            continue

                    offer_data = {
                        "search_keyword": kw,
                        "title": title,
                        "company": company,
                        "location": location_text,
                        "description": description,
                        "job_url": job_url,
                        "apply_url": apply_url,  # parfois vide si login / flux interne
                        "extract_date": datetime.now().strftime("%Y-%m-%d"),
                    }

                    all_offers.append(offer_data)
                    offers_for_kw += 1
                    print(f"[INFO] Offre extraite pour '{kw}'. Total pour ce mot-clé : {offers_for_kw}")
                    human_sleep(1.0, 2.0)

                # fin boucle offres page

                # Si limite d'offres atteinte, on sort du while
                if max_offers_per_kw is not None and offers_for_kw >= max_offers_per_kw:
                    break

                page += 1  # page suivante

        # =========================
        #  SAUVEGARDE JSON
        # =========================
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
#  MAIN
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
        max_offers_per_kw=None,   # ou par ex. 50 pour limiter par mot-clé
        max_pages_per_kw=5,       # nombre max de pages par mot-clé
    )
