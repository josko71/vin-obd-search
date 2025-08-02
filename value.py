import os
import django
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

# Nastavite Django okolje (če je potrebno za zagon izven Django projekta, sicer ga odstranite)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avto_vin_obd_projekt.settings')
# django.setup()

def get_brand_values():
    base_url = "https://www.avto.net/"
    GECKODRIVER_PATH = './drivers/geckodriver' # Prilagodite to pot

    firefox_options = FirefoxOptions()
    # firefox_options.add_argument("--headless") # Lahko pustite vidno za debugiranje
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0")

    driver = None
    try:
        service = Service(executable_path=GECKODRIVER_PATH)
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.implicitly_wait(10)

        driver.get(base_url)
        print(f"Brskalnik uspešno odprl: {base_url}")

        # Obravnavanje piškotkov (ponovi iz prejšnjega odgovora)
        try:
            accept_cookies_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'CybotCookiebotDialogBodyLevelButtonAccept'))
            )
            if accept_cookies_button.is_displayed() and accept_cookies_button.is_enabled():
                accept_cookies_button.click()
                print("Gumb za sprejem piškotkov kliknjen.")
                time.sleep(2)
        except TimeoutException:
            print("Okno za piškotke ni najdeno v določenem času. Nadaljujem.")
        except Exception as e:
            print(f"Napaka pri obdelavi piškotkov: {e}. Nadaljujem.")

        znamke_select_element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'make'))
        )
        print("Najden element 'select' za znamke.")

        options = znamke_select_element.find_elements(By.TAG_NAME, 'option')
        print("\n--- Znamke in njihovi VALUE atributi ---")
        for option in options:
            option_value = option.get_attribute('value')
            option_text = option.text.strip()
            if option_value: # Preveri, če je value atribut sploh prisoten
                 print(f"Tekst: '{option_text}' | Value: '{option_value}'")

    except WebDriverException as e:
        print(f"Napaka WebDriverja: {e}")
    except TimeoutException as e:
        print(f"Časovna omejitev: {e}")
    except Exception as e:
        print(f"Splošna napaka: {e}")
    finally:
        if driver:
            driver.quit()
            print("Brskalnik zaprt.")

if __name__ == "__main__":
    get_brand_values()