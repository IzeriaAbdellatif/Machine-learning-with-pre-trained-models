import time
import json
import re
from datetime import datetime
from urllib.parse import quote_plus
from random import uniform

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================
#  UTILITAIRES GÉNÉRAUX
# =========================

def human_sleep(min_s: float = 2.0, max_s: float = 5.0):
    """Pause aléatoire pour rendre le scraping plus humain."""
    time.sleep(uniform(min_s, max_s))


def build_search_url(keyword: str, location: str) -> str:
    """
    Construit l'URL de recherche Indeed pour la page 1.
    La pagination se fera ensuite en cliquant sur les boutons de pages.
    """
    base_url = "https://ma.indeed.com/jobs"
    q = quote_plus(keyword)
    loc = quote_plus(location)
    return f"{base_url}?q={q}&l={loc}"


def parse_job_count(driver, wait) -> int | None:
    """Récupère le nombre total d'offres affiché par Indeed (si dispo)."""
    try:
        count_el = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.jobsearch-JobCountAndSortPane-jobCount")
            )
        )
        text = count_el.text  # ex : "17 emplois", "201 jobs"
        m = re.search(r"(\d[\d\s]*)", text)
        if not m:
            return None
        num_str = m.group(1).replace(" ", "")
        return int(num_str)
    except Exception:
        return None


# =========================
#  COLLECTE DES URLS PAR PAGE
# =========================

def collect_job_urls_on_page(driver, wait, ul_selector: str, li_selector: str) -> list[str]:
    """
    Sur la page courante :
    - scrolle plusieurs fois jusqu'en bas pour charger toutes les offres,
    - récupère toutes les <li> qui contiennent un <a>,
    - renvoie la liste des href (job_url).
    """

    # Scroll progressif pour charger toutes les offres (lazy loading)
    last_height = 0
    for _ in range(6):  # ~ 5–6 scrolls suffisent en général
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_sleep(1.5, 3.0)
        new_height = driver.execute_script("return document.body.scrollHeight;")
        if new_height == last_height:
            break
        last_height = new_height

    # Récupérer le <ul> principal des offres
    try:
        ul_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ul_selector))
        )
    except Exception:
        print("[WARN] Impossible de trouver le conteneur <ul> des offres sur cette page.")
        return []

    all_li = ul_element.find_elements(By.CSS_SELECTOR, li_selector)

    job_urls = []
    for li in all_li:
        try:
            a_el = li.find_element(By.CSS_SELECTOR, "a")
            href = a_el.get_attribute("href")
            if href:
                job_urls.append(href)
        except Exception:
            # li sans lien (placeholder, tracking, etc.) → on ignore
            continue

    # Optionnel : dédupli dans la page (au cas où la même URL se répète)
    unique_urls = list(dict.fromkeys(job_urls))

    print(f"[INFO] URLs d'offres collectées sur cette page : {len(unique_urls)}")
    return unique_urls


# =========================
#  PAGINATION : CLIC SUR LES PAGES
# =========================

def click_next_page(driver, wait, current_page: int) -> bool:
    """
    Trouve et clique sur le <li> correspondant à la page suivante (current_page + 1)
    dans la pagination Indeed.
    Retourne True si le clic a été effectué, False sinon (pas de page suivante).
    """
    try:
        # descendre jusqu'à la pagination
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_sleep(1.5, 2.5)

        # Certaines versions utilisent 'serp-page-z64vyd', d'autres 'page-z64vyd'
        pagination_ul = None
        for css in [
            "ul.serp-page-z64vyd.eu4oa1w0",
            "ul.page-z64vyd.eu4oa1w0",
        ]:
            try:
                pagination_ul = driver.find_element(By.CSS_SELECTOR, css)
                break
            except Exception:
                continue

        if pagination_ul is None:
            print("[INFO] Pagination non trouvée (ul), fin de pagination.")
            return False

        li_pages = pagination_ul.find_elements(By.CSS_SELECTOR, "li.serp-page-8umzvb.eu4oa1w0")

        # filtrer les numéros uniquement (ignorer « Suivant », « Précédent », etc.)
        numeric_buttons = [li for li in li_pages if li.text.strip().isdigit()]

        next_page_text = str(current_page + 1)
        next_button = None
        for li in numeric_buttons:
            if li.text.strip() == next_page_text:
                next_button = li
                break

        if not next_button:
            print(f"[INFO] Aucun bouton pour la page {next_page_text} (fin de pagination).")
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_button)
        human_sleep(0.8, 1.5)
        driver.execute_script("arguments[0].click();", next_button)
        human_sleep(3.0, 4.5)
        print(f"[INFO] Passage à la page {next_page_text}")
        return True

    except Exception:
        print("[INFO] Pagination non trouvée ou clic impossible (fin de pagination).")
        return False


# =========================
#  FONCTION PRINCIPALE
# =========================

def scrape_indeed_offers(
    keywords: list[str],
    location: str,
    output_json: str,
    max_offers_per_kw: int | None = None,
    max_pages_per_kw: int | None = None,
):
    """
    Scrape les offres Indeed pour plusieurs mots-clés (stages + jobs IT).

    - keywords : liste de requêtes (ex: ["stage data science", "AI engineer", ...])
    - location : ex. "Maroc"
    - max_offers_per_kw : nombre max d'offres à collecter par mot-clé
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
        # ⚠ Si besoin : uc.Chrome(options=options, version_main=142)
        driver = uc.Chrome(options=options, version_main=142)
        wait = WebDriverWait(driver, 15)

        ul_selector = "ul.css-pygyny.eu4oa1w0"
        li_selector = "li.css-1ac2h1w.eu4oa1w0"

        # ---------- Login manuel ----------
        print("[INFO] Ouverture initiale pour connexion manuelle à Indeed...")
        driver.get("https://ma.indeed.com/")
        human_sleep(5, 8)
        input("[ACTION] Connecte-toi à Indeed dans la fenêtre, puis appuie sur Entrée ici pour commencer le scraping... ")

        # ---------- Boucle sur les mots-clés ----------
        for kw in keywords:
            print("\n" + "=" * 60)
            print(f"[INFO] Mot-clé de recherche : {kw}")

            offers_for_kw = 0

            # Charger la page 1
            search_url = build_search_url(kw, location)
            print(f"[INFO] Page 1 URL : {search_url}")
            driver.get(search_url)
            human_sleep(4, 7)

            # Nombre d'offres (info)
            job_count = parse_job_count(driver, wait)
            if job_count is not None:
                print(f"[INFO] Nombre total d'offres annoncé pour '{kw}' : {job_count}")
            else:
                print(f"[INFO] Impossible de déterminer le nombre total d'offres pour '{kw}'")

            current_page = 1

            # Boucle pagination via clics
            while True:
                print(f"\n[INFO] Scraping page {current_page} pour '{kw}'")

                # 1) Récupérer toutes les URLs d'offres sur cette page
                page_job_urls = collect_job_urls_on_page(
                    driver, wait, ul_selector, li_selector
                )

                if not page_job_urls:
                    print("[INFO] Aucune offre cliquable sur cette page, on arrête pour ce mot-clé.")
                    break

                new_offers_in_page = 0

                # 2) Boucle sur les URLs d'offres (on NE déduplique PAS entre mots-clés)
                for idx, job_url in enumerate(page_job_urls, start=1):
                    if max_offers_per_kw is not None and offers_for_kw >= max_offers_per_kw:
                        print(f"[INFO] Limite d'offres atteinte pour '{kw}'.")
                        break

                    print(f"[INFO] ({idx}/{len(page_job_urls)}) Scraping offre : {job_url}")
                    driver.get(job_url)
                    human_sleep(2, 4)

                    # ----- Extraction des informations -----

                    # Title
                    title = ""
                    for css in [
                        "h1.jobsearch-JobInfoHeader-title",
                        "div.jobsearch-JobInfoHeader-title-container",
                    ]:
                        try:
                            title = driver.find_element(By.CSS_SELECTOR, css).text
                            if title:
                                break
                        except Exception:
                            continue

                    # Company
                    company = ""
                    for css in [
                        "span.css-qcqa6h.e1wnkr790",
                        "div.jobsearch-CompanyInfoWithoutHeaderImage div",
                    ]:
                        try:
                            company = driver.find_element(By.CSS_SELECTOR, css).text
                            if company:
                                break
                        except Exception:
                            continue

                    # Location
                    location_text = ""
                    for css in [
                        "div#jobLocationText",
                        "div.jobsearch-CompanyInfoWithoutHeaderImage + div",
                    ]:
                        try:
                            location_text = driver.find_element(By.CSS_SELECTOR, css).text
                            if location_text:
                                break
                        except Exception:
                            continue

                    # Description
                    try:
                        description = driver.find_element(
                            By.CSS_SELECTOR, "div#jobDescriptionText"
                        ).text
                    except Exception:
                        description = ""

                    # Lien de postulation
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
                        "apply_url": apply_url,
                        "extract_date": datetime.now().strftime("%Y-%m-%d"),
                    }

                    all_offers.append(offer_data)
                    offers_for_kw += 1
                    new_offers_in_page += 1

                    print(f"[INFO] Offre extraite pour '{kw}'. Total pour ce mot-clé : {offers_for_kw}")

                # Fin boucle offres de la page
                if max_offers_per_kw is not None and offers_for_kw >= max_offers_per_kw:
                    print(f"[INFO] Limite d'offres atteinte pour '{kw}', on n'avance plus dans les pages.")
                    break

                if max_pages_per_kw is not None and current_page >= max_pages_per_kw:
                    print(f"[INFO] max_pages_per_kw={max_pages_per_kw} atteint pour '{kw}'.")
                    break

                if new_offers_in_page == 0:
                    print("[INFO] Aucune nouvelle offre sur cette page, arrêt de la pagination pour ce mot-clé.")
                    break

                # 3) Cliquer sur la page suivante
                has_next = click_next_page(driver, wait, current_page)
                if not has_next:
                    break
                current_page += 1

        # ---------- Sauvegarde JSON ----------
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
        "stage data science",
        "stage machine learning",
        "stage data engineer",
        "software engineering internship",
        "AI internship",
        "Data scientist",
        "Ai engineer",
        "software developer",
        "machine learning engineer",
        "data engineer",
    ]

    scrape_indeed_offers(
        keywords=keywords,
        location="Maroc",
        output_json="indeed_stages_data_ia.json",
        max_offers_per_kw=None,   # ex: 50 si tu veux limiter par mot-clé
        max_pages_per_kw=None,    # ex: 3 pour ne pas dépasser 3 pages par mot-clé
    )
