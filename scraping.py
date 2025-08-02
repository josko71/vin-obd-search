import os
import django
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException

# Nastavite Django okolje
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avto_vin_obd_projekt.settings')
django.setup()

# Uvozite modele po tem, ko je Django nastavljen
from vozila.models import Znamka, CarModel, Vozilo 

def scrape_znamke_in_modele_avto_net_selenium():
    base_url = "https://www.avto.net/"
    print(f"Začenjam scraping znamk in modelov iz: {base_url} z uporabo Seleniuma in Firefoxa.")

    # Prilagodite to pot do vašega geckodriverja
    # Prepričajte se, da je geckodriver v isti mapi kot ta skripta ali podajte absolutno pot
    GECKODRIVER_PATH = './drivers/geckodriver' 

    firefox_options = FirefoxOptions()
    # Zakomentirajte naslednjo vrstico (dodajte # na začetek vrstice), če želite videti brskalnik med delovanjem
    # firefox_options.add_argument("--headless") # Headless način za delovanje v ozadju
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0")
    firefox_options.log.level = "trace" # Povečamo log level za več informacij

    driver = None

    try:
        service = Service(executable_path=GECKODRIVER_PATH)
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.implicitly_wait(10) # Splošno implicitno čakanje

        driver.get(base_url)
        print(f"Brskalnik uspešno odprl: {base_url}")

        # --- KORAK: SPREJEMANJE PIŠKOTKOV (AGRESIVNEJŠE) ---
        print("Preverjam prisotnost okna za piškotke...")
        try:
            # Počakaj, da gumb postane klikljiv
            accept_cookies_button = WebDriverWait(driver, 20).until( # Povečal čas čakanja
                EC.element_to_be_clickable((By.ID, 'CybotCookiebotDialogBodyLevelButtonAccept'))
            )
            
            if accept_cookies_button.is_displayed() and accept_cookies_button.is_enabled():
                print("Gumb za sprejem piškotkov je viden in omogočen.")
                
                try:
                    accept_cookies_button.click()
                    print("Gumb za sprejem piškotkov kliknjen (standardno).")
                except ElementClickInterceptedException:
                    print("Gumb za piškotke je prekrit, poskušam klikniti z JavaScriptom.")
                    driver.execute_script("arguments.click();", accept_cookies_button)
                    print("Gumb za sprejem piškotkov kliknjen (JavaScript).")
                
                # Dolg premor, da se piškotki popolnoma odstranijo in DOM stabilizira
                time.sleep(3) # Kratek premor po kliku
                
                # Poskusimo odstraniti celoten dialog za piškotke iz DOM-a z JavaScriptom
                try:
                    driver.execute_script("var element = document.getElementById('CybotCookiebotDialog'); if(element) element.remove();")
                    print("Dialog za piškotke odstranjen iz DOM-a z JavaScriptom.")
                except Exception as e_remove_dialog:
                    print(f"Napaka pri odstranjevanju dialoga za piškotke z JavaScriptom: {e_remove_dialog}. Nadaljujem.")

                # Počakamo, da se prekrivni element (če je bil) popolnoma umakne
                try:
                    WebDriverWait(driver, 15).until_not( # Povečal čas čakanja
                        EC.presence_of_element_located((By.ID, 'CybotCookiebotDialogPoweredbyLink'))
                    )
                    print("Prekrivni element piškotkov je izginil.")
                except TimeoutException:
                    print("Opozorilo: Prekrivni element piškotkov ni izginil po kliku v določenem času, nadaljujem.")
                
                time.sleep(2) # Dodaten kratek premor za stabilizacijo

            else:
                print("Gumb za piškotke ni bil viden ali omogočen, nadaljujem brez interakcije s piškotki.")

        except TimeoutException:
            print("Okno za piškotke ni najdeno v določenem času. Nadaljujem.")
        except Exception as e:
            print(f"Nepričakovana napaka pri obdelavi piškotkov: {e}. Nadaljujem.")
        # -------------------------------------------

        # --- KORAK 1: PRIDOBIVANJE ZNAMK ---
        # Počakamo na prisotnost elementa 'make'
        znamke_select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'make'))
        )
        print("Najden element 'select' za znamke.")

        options = znamke_select_element.find_elements(By.TAG_NAME, 'option')
        znamke_za_obdelavo = []
        
        # Logika za obdelavo VSEH znamk (odstranjena omejitev na testne znamke)
        for option in options:
            option_value = option.get_attribute('value')
            znamka_ime = option.text.strip() # Uporabimo text namesto value, saj je bolj berljiv
            
            # Preverimo, če je opcija veljavna in omogočena
            if option_value and znamka_ime and option.is_enabled() and \
               znamka_ime not in ["", "Vsi", "Vse znamke", "znamka ni na seznamu", "- Najpopularnejše znamke:", "- Vse znamke:"]: # Dodatna preverjanja za neveljavne opcije
                
                znamka_obj, created = Znamka.objects.get_or_create(ime=znamka_ime)
                if created:
                   print(f"  Shranjena nova znamka: {znamka_ime}")
                znamke_za_obdelavo.append(znamka_obj)
            # else:
            #    print(f"  Preskakujem neveljavno opcijo znamke: '{znamka_ime}' (value: '{option_value}')") # Za debugiranje

        if not znamke_za_obdelavo:
            print("Opozorilo: Ni najdenih veljavnih znamk za obdelavo. Preverite dostopnost opcij.")

        print(f"Scraping znamk zaključen. Najdenih znamk: {len(znamke_za_obdelavo)}")
        time.sleep(2)

        # --- KORAK 2: PRIDOBIVANJE MODELOV ZA VSAKO ZNAMKO ---
        for znamka_obj in znamke_za_obdelavo:
            print(f"\n---> Obdelujem znamko: {znamka_obj.ime} <---")
            
            try:
                # Vedno se vrnemo na osnovni URL za konsistentnost za vsako znamko
                driver.get(base_url)
                
                # Počakamo, da so elementi ponovno prisotni na strani
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'make'))) 

                # Ponovno lociramo element znamke, da preprečimo StaleElementReferenceException
                znamke_select_element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, 'make'))
                )
                
                # Izberemo znamko z JavaScriptom (najbolj robustna metoda za izogib ElementClickInterceptedException)
                target_option_value = None
                for option in znamke_select_element.find_elements(By.TAG_NAME, 'option'):
                    if option.text.strip() == znamka_obj.ime:
                        target_option_value = option.get_attribute('value')
                        break
                
                if target_option_value:
                    driver.execute_script(f"document.getElementById('make').value = '{target_option_value}';")
                    driver.execute_script(f"document.getElementById('make').dispatchEvent(new Event('change'));")
                    print(f"  Znamka '{znamka_obj.ime}' (value: '{target_option_value}') izbrana z JavaScriptom.")
                else:
                    print(f"  Napaka: Ne morem najti vrednosti za znamko '{znamka_obj.ime}'. Preskakujem obdelavo modelov za to znamko.")
                    continue
                
                time.sleep(3) # Kratek premor, da se AJAX zahteva dokonča in modeli naložijo

                # *** ROBUSTNO ČAKANJE NA MODELE ***
                print(f"  Čakam, da se naložijo modeli za '{znamka_obj.ime}'...")

                model_select_element = None 
                select_model_obj = None

                model_options_loaded = False
                total_wait_time = 60 # Povečan čas čakanja za modele
                start_time = time.time()

                while not model_options_loaded and (time.time() - start_time) < total_wait_time:
                    try:
                        # Počakamo na prisotnost elementa 'model'
                        model_select_element = WebDriverWait(driver, 15).until( 
                            EC.presence_of_element_located((By.ID, 'model'))
                        )
                        select_model_obj = Select(model_select_element) 

                        # Preverimo, če ima seznam modelov več kot eno opcijo (razen 'Vsi modeli')
                        # ali če ima eno opcijo, ki ni "Vsi modeli" in ni "modela ni na seznamu"
                        if len(select_model_obj.options) > 1 or \
                           (len(select_model_obj.options) == 1 and 
                            select_model_obj.options.text.strip() not in ["Vsi modeli", "modela ni na seznamu"]):
                            model_options_loaded = True
                            print(f"  Padajoči seznam modelov za '{znamka_obj.ime}' ima napolnjene opcije.")
                        else:
                            print(f"  Opcije modelov za '{znamka_obj.ime}' še niso napolnjene (trenutno {len(select_model_obj.options)} opcij). Čakam...")
                            time.sleep(1) # Kratek premor pred ponovnim preverjanjem

                    except StaleElementReferenceException:
                        print(f"  Opozorilo: StaleElementReferenceException pri elementu modela za '{znamka_obj.ime}'. Poskušam ponovno po kratkem počitku.")
                        time.sleep(1) 
                    except TimeoutException:
                        print(f"  Opozorilo: Timeout pri iskanju elementa modela za '{znamka_obj.ime}'. Poskušam ponovno po kratkem počitku.")
                        time.sleep(1) 
                    except Exception as e_check_model_load:
                        print(f"  Nepričakovana napaka med čakanjem na nalaganje modelov za '{znamka_obj.ime}': {e_check_model_load}. Poskušam ponovno.")
                        time.sleep(1)

                if not model_options_loaded:
                    print(f"  Opozorilo: Modeli za znamko '{znamka_obj.ime}' se niso naložili po {total_wait_time} sekundah. Preskakujem.")
                    driver.save_screenshot(f"models_not_loaded_{znamka_obj.ime}.png")
                    continue # Preskoči to znamko in pojdi na naslednjo

                # Nadaljevanje po uspešnem nalaganju modelov (ne glede na to, ali je bil specificiran model ali splošno čakanje)
                # Zagotovimo, da je select_model_obj inicializiran, če ni bil v zgornji zanki
                if select_model_obj is None: 
                     model_select_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'model')))
                     select_model_obj = Select(model_select_element)


                # Pridobimo opcije in jih shranimo (BOLJ ROBUSTNO ITERIRANJE)
                # *** KLJUČNA SPREMEMBA: Pridobimo vse opcije v enem koraku, da preprečimo StaleElementReferenceException ***
                model_options_data = []
                try:
                    current_options = select_model_obj.find_elements(By.TAG_NAME, 'option')
                    for option in current_options:
                        model_text = option.text.strip()
                        model_value = option.get_attribute('value')
                        if model_text and model_text not in ["Vsi modeli", "modela ni na seznamu", "- Najpopularnejše znamke:", "- Vse znamke:"]:
                            model_options_data.append({'text': model_text, 'value': model_value})
                except StaleElementReferenceException:
                    print(f"  Opozorilo: StaleElementReferenceException med pridobivanjem opcij za '{znamka_obj.ime}'. Poskušam ponovno pridobiti opcije.")
                    # Če se zgodi StaleElementReferenceException tukaj, poskusimo ponovno najti select_model_obj
                    model_select_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'model')))
                    select_model_obj = Select(model_select_element)
                    current_options = select_model_obj.find_elements(By.TAG_NAME, 'option')
                    for option in current_options:
                        model_text = option.text.strip()
                        model_value = option.get_attribute('value')
                        if model_text and model_text not in ["Vsi modeli", "modela ni na seznamu", "- Najpopularnejše znamke:", "- Vse znamke:"]:
                            model_options_data.append({'text': model_text, 'value': model_value})
                except Exception as e_get_options:
                    print(f"  Napaka pri pridobivanju opcij modelov za '{znamka_obj.ime}': {e_get_options}. Preskakujem shranjevanje modelov.")
                    continue # Preskoči shranjevanje modelov za to znamko

                if not model_options_data:
                    print(f"  Opozorilo: Ni veljavnih modelov za shranjevanje za znamko '{znamka_obj.ime}'.")

                for model_data in model_options_data:
                    model_ime = model_data['text']
                    try:
                        # Uporabimo unique_together = ('znamka', 'ime') v modelu CarModel,
                        # da preprečimo podvojene vnose, če se isti model pojavi večkrat.
                        model_obj, created = CarModel.objects.get_or_create(znamka=znamka_obj, ime=model_ime)
                        if created:
                            print(f"    Shranjena nova modela: {znamka_obj.ime} - {model_ime}")
                        # else:
                        #    print(f"    Model '{model_ime}' za znamko '{znamka_obj.ime}' že obstaja.")
                    except Exception as e_model_save: 
                        print(f"    Napaka pri shranjevanju modela '{model_ime}' za znamko '{znamka_obj.ime}': {e_model_save}. Preskakujem.")
                        continue 
                
                # --- Testni klik na prvi model in iskanje (neobvezno za samo shranjevanje modelov) ---
                # Ta del kode je bolj za preverjanje funkcionalnosti, kot za pridobivanje vseh podatkov.
                # Če želite samo zbrati znamke in modele, lahko ta blok zakomentirate.
                if model_options_data: # Preverimo, ali obstaja vsaj en veljaven model
                    first_actual_model_value = model_options_data['value']
                    first_actual_model_text = model_options_data['text']

                    # Izberemo prvi model z JavaScriptom
                    try:
                        driver.execute_script(f"document.getElementById('model').value = '{first_actual_model_value}';")
                        driver.execute_script(f"document.getElementById('model').dispatchEvent(new Event('change'));") 
                        print(f"  Model '{first_actual_model_text}' (value: '{first_actual_model_value}') izbran z JavaScriptom.")
                    except Exception as e_js_select_model:
                        print(f"  Napaka pri izbiri modela '{first_actual_model_text}' z JavaScriptom: {e_js_select_model}.")
                        # Če izbira modela ne uspe, nadaljujemo na naslednjo znamko, da ne blokiramo celotnega procesa
                        continue 
                    
                    time.sleep(1) 

                    # Klik na gumb 'Iskanje vozil' z JavaScriptom (najbolj robustno)
                    try:
                        search_button = WebDriverWait(driver, 15).until( 
                            EC.presence_of_element_located((By.NAME, 'B1')) 
                        )
                        driver.execute_script("arguments.click();", search_button)
                        print(f"  Gumb 'Iskanje vozil' kliknjen z JavaScriptom.")
                    except TimeoutException:
                        print(f"  Gumb 'Iskanje vozil' ni bil najden v določenem času. Preskakujem klik.")
                    except Exception as click_error:
                        print(f"  Napaka pri klikanju gumba 'Iskanje vozil': {click_error}. Preskakujem klik.")

                    # Počakamo, da se URL spremeni na stran z rezultati
                    try:
                        WebDriverWait(driver, 20).until(EC.url_contains("Ads/results.asp"))
                        print(f"  URL se je uspešno spremenil na stran z rezultati: {driver.current_url}")
                        time.sleep(3) 
                        # Tukaj bi lahko dodali kodo za scraping podatkov o vozilih na strani z rezultati
                    except TimeoutException:
                        print(f"  Opozorilo: URL se ni spremenil na Ads/results.asp v določenem času po kliku na iskanje za znamko {znamka_obj.ime} in model {first_actual_model_text}.")
                        driver.save_screenshot(f"url_change_timeout_{znamka_obj.ime}_{first_actual_model_text}.png")

                    print(f"  Končana obdelava znamke {znamka_obj.ime} in modela {first_actual_model_text}.")

                else:
                    print(f"  Ni veljavnih modelov za izbiro in iskanje za znamko '{znamka_obj.ime}'.")
                    time.sleep(1) 

            except TimeoutException as te:
                print(f"  Časovna omejitev: Težava pri nalaganju elementov za znamko '{znamka_obj.ime}'. Napaka: {te}")
                driver.save_screenshot(f"timeout_screenshot_{znamka_obj.ime}.png") 
                
                try:
                    current_model_select = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'model')))
                    current_select_obj = Select(current_model_select)
                    if current_select_obj.options:
                        print(f"    Trenutne opcije modelov za '{znamka_obj.ime}' (debug): {[opt.text for opt in current_select_obj.options]}")
                    else:
                        print(f"    Padajoči seznam modelov za '{znamka_obj.ime}' je prazen.")
                except Exception as ex:
                    print(f"    Napaka pri pridobivanju trenutnih opcij modelov za debugiranje: {ex}")

                continue 
            except Exception as e: 
                print(f"  Splošna napaka pri obdelavi znamke '{znamka_obj.ime}' ali pridobivanju njenih modelov: {e}")
                driver.save_screenshot(f"error_general_{znamka_obj.ime}.png")
                continue 

    except WebDriverException as e:
        print(f"Napaka WebDriverja: {e}")
        print("Preverite pot do geckodriverja in njegovo združljivost z različico Firefoxa.")
        print("Preverite tudi, ali je Firefox nameščen in na voljo v PATH ali z uporabo FirefoxBinary.")
    except TimeoutException as e:
        print(f"Časovna omejitev: Stran se ni naložila ali ključni element ni bil najden v določenem času. {e}")
        driver.save_screenshot("final_timeout_screenshot.png")
    except Exception as e:
        print(f"Splošna napaka pri scrapingu: {e}")
        driver.save_screenshot("final_error_screenshot.png")
    finally:
        if driver:
            driver.quit()
            print("Brskalnik zaprt.")

if __name__ == "__main__":
    scrape_znamke_in_modele_avto_net_selenium()
    print("Scraping zaključeno.")