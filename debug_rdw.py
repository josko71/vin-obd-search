import requests
import json

RDW_DOMAIN = "opendata.rdw.nl"
RDW_DATASET_ID = "m9d7-ebf2" # Preverite, da je to res ID, ki ga uporabljate v rdw_importer.py
APP_TOKEN = "MF645CIo5eU72jWfRO5eZHGPH" # Vnesite vaš dejanski, preverjen token

url = f"https://{RDW_DOMAIN}/resource/{RDW_DATASET_ID}"

# App Token se pogosto posreduje v glavi HTTP zahtevka
headers = {
    "X-App-Token": APP_TOKEN,
    "Accept": "application/json" # Zahtevamo JSON odgovor
}

# Parametri za testni klic (želimo le nekaj osebnih avtomobilov)
params = {
    "$limit": 10,
    "$where": "voertuigsoort = 'Personenauto'"
}

print(f"Poskušam dostopati do URL-ja: {url}")
print(f"Z ID-jem podatkovne zbirke: {RDW_DATASET_ID}")
print(f"Z uporabo APP_TOKEN (prvih 5 znakov): {APP_TOKEN[:5]}*****")

try:
    response = requests.get(url, headers=headers, params=params, timeout=10) # Dodamo timeout
    response.raise_for_status() # Sproži izjemo za HTTP napake (4xx ali 5xx)

    data = response.json()

    if data:
        print("\nUspešno pridobljeni podatki (prvih 10 zapisov):")
        for i, record in enumerate(data):
            merk = record.get('merk', 'N/A')
            handelsbenaming = record.get('handelsbenaming', 'N/A')
            voertuigsoort = record.get('voertuigsoort', 'N/A')
            print(f"{i+1}. Znamka: {merk}, Model: {handelsbenaming}, Tip: {voertuigsoort}")
    else:
        print("API je vrnil prazen seznam. Ni podatkov za prikaz z danimi parametri.")

except requests.exceptions.HTTPError as e:
    print(f"\nHTTP Napaka pri API klicu: {e}")
    print(f"Status koda: {e.response.status_code}")
    print(f"Odgovor API-ja (če obstaja): {e.response.text}")
except requests.exceptions.ConnectionError as e:
    print(f"\nNapaka pri povezavi z API-jem (preverite internetno povezavo ali URL): {e}")
except requests.exceptions.Timeout as e:
    print(f"\nČasovna omejitev pri API klicu (strežnik se ni odzval pravočasno): {e}")
except requests.exceptions.RequestException as e:
    print(f"\nSplošna napaka pri zahtevi: {e}")
except json.JSONDecodeError as e:
    print(f"\nNapaka pri dekodiranju JSON odgovora. API morda ni vrnil veljavnega JSON-a: {e}")
    print(f"Neveljaven odgovor: {response.text}")
except Exception as e:
    print(f"\nPrišlo je do nepričakovane napake: {e}")