"""
Proiect: Testarea unei aplicații web - Extragere Evenimente Campus Virtual
Echipa: 12-E4
Studenti: CIORÎIA I. CĂTĂLIN-THEODOR, NASTASIU D. VICTOR-LUCIAN
Tema: D8-T1

Descriere:
Acest script se conectează automat la platforma Campus Virtual UPT (cv.upt.ro)
folosind autentificarea Moodle standard. După login, navighează la secțiunea
de evenimente și extrage numele și data evenimentelor listate pe pagina de calendar.
Informațiile extrase sunt salvate într-un fișier text.

Surse de inspirație conceptuală:
- Selenium Documentation: https://www.selenium.dev/documentation/
- Articole despre automatizarea login-ului și web scraping cu Selenium și Python.
- Youtube
- W3schools
"""

import os
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from dotenv import load_dotenv

LOGIN_URL = "https://cv.upt.ro/login/index.php"
CALENDAR_PAGE_TARGET_URL_PART = "https://cv.upt.ro/calendar/view.php"
ID_USERNAME_FIELD = "username"
ID_PASSWORD_FIELD = "password"
ID_LOGIN_BUTTON = "loginbtn"
ID_LOGIN_CONFIRMATION_ELEMENT = "page-my-index"
XPATH_DASHBOARD_EVENTS_LINK = "//a[@title='Evenimente' and contains(@href, 'https://cv.upt.ro/calendar/view.php')]"
CSS_CALENDAR_EVENT_ITEM = 'div[data-type="event"].event'
CSS_CALENDAR_EVENT_NAME = 'div.box.card-header h3.name'
CSS_CALENDAR_EVENT_DATE = 'div.description.card-body div.row:nth-of-type(1) div.col-11'
WAIT_TIMEOUT = 20

def initializare_driver_chrome():
    print("Inițializare WebDriver Chrome...")
    try:
        opts = webdriver.ChromeOptions()
        #opts.add_argument("--headless")
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-gpu")
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        serv = Service(ChromeDriverManager().install())
        driver_instance = webdriver.Chrome(service=serv, options=opts)
        print("WebDriver Chrome inițializat cu succes.")
        return driver_instance
    except Exception as e:
        print(f"EROARE FATALĂ la inițializarea WebDriver: {e}")
        return None
def functie_autentificare(driver, username, parola):
    print(f"Autentificare în curs pentru utilizatorul: {username}...")
    try:
        driver.get(LOGIN_URL)
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, ID_USERNAME_FIELD))).send_keys(username)
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, ID_PASSWORD_FIELD))).send_keys(parola)
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.ID, ID_LOGIN_BUTTON))).click()
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, ID_LOGIN_CONFIRMATION_ELEMENT)))
        WebDriverWait(driver, WAIT_TIMEOUT).until_not(EC.url_contains("/login/index.php"))
        print(f"Autentificare reușită. Pagina curentă: {driver.current_url}")
        return True
    except TimeoutException:
        print("EROARE: Timeout la autentificare.")
        return False
    except Exception as e:
        print(f"EROARE neașteptată la autentificare: {e}")
        return False
def functie_extragere_evenimente(driver):
    print("Extragere evenimente...")
    evenimente_gasite = []
    try:
        print(f"Pagina curentă (Dashboard): {driver.current_url}")
        print(f"Căutare link 'Evenimente' (XPATH: {XPATH_DASHBOARD_EVENTS_LINK})...")
        link_calendar_element = WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, XPATH_DASHBOARD_EVENTS_LINK)))
        print("Link 'Evenimente' găsit și clickabil.")
        link_calendar_element.click()
        print("Click pe link-ul 'Evenimente' efectuat/încercat.")
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.url_contains(CALENDAR_PAGE_TARGET_URL_PART))
        print(f"Navigat cu succes la pagina calendarului: {driver.current_url}")
    except TimeoutException:
        print(f"EROARE TIMEOUT: Link-ul 'Evenimente' (XPATH: {XPATH_DASHBOARD_EVENTS_LINK}) nu a fost găsit sau nu a devenit clickabil.")
        return evenimente_gasite
    except ElementClickInterceptedException:
        print(f"EROARE: Click-ul pe link-ul 'Evenimente' a fost interceptat de un alt element.")
        print(f"Pagina curentă: {driver.current_url}. Încearcă să identifici elementul care blochează.")
        return evenimente_gasite
    except Exception as e_nav:
        print(f"EROARE la navigarea spre pagina de calendar: {e_nav}")
        return evenimente_gasite
    if any(val.startswith("REPLACE_ME_") for val in
           [CSS_CALENDAR_EVENT_ITEM, CSS_CALENDAR_EVENT_NAME, CSS_CALENDAR_EVENT_DATE]):
        print("EROARE CRITICĂ: Selectorii CSS pentru extragerea evenimentelor (CSS_CALENDAR_...) trebuie actualizați!")
        return evenimente_gasite
    try:
        print(f"Așteptare item-uri de eveniment pe pagina de calendar (selector item: '{CSS_CALENDAR_EVENT_ITEM}')...")
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_CALENDAR_EVENT_ITEM)))
        elemente_eveniment_html = driver.find_elements(By.CSS_SELECTOR, CSS_CALENDAR_EVENT_ITEM)
        if not elemente_eveniment_html:
            print("Nu s-au găsit item-uri de eveniment pe pagina de calendar.")
            return evenimente_gasite
        print(f"S-au găsit {len(elemente_eveniment_html)} item-uri de eveniment. Se procesează...")
        for idx, item_html in enumerate(elemente_eveniment_html, 1):
            nume = "N/A"
            data = "N/A"
            try:
                nume = item_html.find_element(By.CSS_SELECTOR, CSS_CALENDAR_EVENT_NAME).text.strip()
            except NoSuchElementException:
                pass
            try:
                data = item_html.find_element(By.CSS_SELECTOR, CSS_CALENDAR_EVENT_DATE).text.strip()
            except NoSuchElementException:
                pass
            if not nume.startswith("N/A"):
                evenimente_gasite.append({"nume": nume, "data": data})
                print(f"      + Extras: '{nume}' | Data: '{data}'")
    except TimeoutException:
        print(f"EROARE TIMEOUT la căutarea item-urilor de eveniment (selector: '{CSS_CALENDAR_EVENT_ITEM}').")
    except Exception as e_extract:
        print(f"EROARE neașteptată la extragerea evenimentelor de pe pagina de calendar: {e_extract}")
    print(f"Extragere finalizată. Total evenimente găsite: {len(evenimente_gasite)}.")
    return evenimente_gasite
def functie_salvare_fisier(username, evenimente):
    if not evenimente:
        print("Nu există evenimente de salvat.")
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_username = "".join(c if c.isalnum() else "_" for c in username)
    filename = f"{safe_username}_{ts}.txt"
    print(f"Salvare evenimente în fișierul '{filename}'...")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Evenimente Campus Virtual pentru: {username}\n")
            f.write(f"Extrase la: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n")
            f.write("=" * 40 + "\n\n")
            for idx, ev in enumerate(evenimente, 1):
                f.write(f"Eveniment {idx}:\n")
                f.write(f"  Nume: {ev.get('nume', 'N/A')}\n")
                f.write(f"  Data: {ev.get('data', 'N/A')}\n")
                f.write("---\n")
        print("Evenimente salvate cu succes.")
    except IOError as e:
        print(f"EROARE I/O la salvarea fișierului: {e}")
    except Exception as e:
        print(f"EROARE neașteptată la salvarea fișierului: {e}")
def main():
    print("--- START SCRIPT EXTRAGERE EVENIMENTE CV ---")
    load_dotenv()
    user = os.getenv("CAMPUS_USERNAME")
    parola = os.getenv("CAMPUS_PASSWORD")
    if not user or not parola:
        print("EROARE: CAMPUS_USERNAME sau CAMPUS_PASSWORD nu sunt definite în fișierul .env.")
        return
    print(f"Se va utiliza username-ul: {user} (parola a fost încărcată).")
    driver = None
    try:
        driver = initializare_driver_chrome()
        if not driver: return
        if functie_autentificare(driver, user, parola):
            lista_evenimente = functie_extragere_evenimente(driver)
            functie_salvare_fisier(user, lista_evenimente)
        else:
            print("Autentificarea a eșuat.")
    except Exception as e_global:
        print(f"A apărut o eroare globală în script: {e_global}")
    finally:
        if driver:
            print("Închidere WebDriver...")
            driver.quit()
        print("--- SFÂRȘIT SCRIPT ---")
def functie_autentificare(driver, username, parola):
    print(f"Autentificare în curs pentru utilizatorul: {username}...")
    try:
        driver.get(LOGIN_URL)
        print(f"PAS 1: Navigat la: {LOGIN_URL}")
        print("PAS 2: Așteptare câmp username...")
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, ID_USERNAME_FIELD))).send_keys(username)
        print("PAS 2: Username introdus.")
        print("PAS 3: Așteptare câmp parolă...")
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, ID_PASSWORD_FIELD))).send_keys(parola)
        print("PAS 3: Parola introdusă.")
        print("PAS 4: Așteptare buton login clickabil...")
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.ID, ID_LOGIN_BUTTON))).click()
        print("PAS 4: Buton de login apăsat.")
        print(f"PAS 5: Așteptare element confirmare login (ID: {ID_LOGIN_CONFIRMATION_ELEMENT}). URL curent: {driver.current_url}")
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, ID_LOGIN_CONFIRMATION_ELEMENT)))
        print(f"PAS 5: Element confirmare login găsit. URL curent: {driver.current_url}")
        print("PAS 6: Așteptare schimbare URL (să nu mai conțină '/login/index.php')...")
        WebDriverWait(driver, WAIT_TIMEOUT).until_not(EC.url_contains("/login/index.php"))
        print(f"PAS 6: Autentificare reușită. Pagina curentă: {driver.current_url}")
        return True
    except TimeoutException as e:
        print(f"EROARE: Timeout la autentificare. Detalii excepție: {e}")
        print(f"Pagina curentă la momentul erorii: {driver.current_url}")
        return False
    except Exception as e:
        print(f"EROARE neașteptată la autentificare: {e}")
        return False
if __name__ == "__main__":
    main()