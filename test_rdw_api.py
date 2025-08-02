import requests

RDW_DOMAIN = "opendata.rdw.nl"
RDW_DATASET_ID = "m8mv-xtjm"
APP_TOKEN = "UVsQU5u8wr4RLiHXNaQOpknbs" # Uporabi svoj token tukaj!

url = f"https://{RDW_DOMAIN}/resource/{RDW_DATASET_ID}.json"
headers = {"X-App-Token": APP_TOKEN} # App Token se pogosto pošilja v headerjih
params = {
    "$limit": 10,
    "$where": "voertuigsoort = 'Personenauto'"
}

print(f"Povezujem se z: {url}")
print(f"S parametri: {params}")
print(f"Z App Tokenom (v glavi): {APP_TOKEN[:5]}...{APP_TOKEN[-5:]}") # Prikaži del tokena

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status() # Sproži izjemo za HTTP napake
    data = response.json()

    if data:
        print("\nUspešno pridobljeni podatki:")
        for item in data:
            print(f"- Znamka: {item.get('merk', 'N/A')}, Model: {item.get('handelsbenaming', 'N/A')}")
    else:
        print("API je vrnil prazen seznam. Ni podatkov za prikaz.")

except requests.exceptions.RequestException as e:
    print(f"Napaka pri API klicu: {e}")
    print(f"Status koda: {e.response.status_code if e.response else 'N/A'}")
    print(f"Odgovor API-ja: {e.response.text if e.response else 'N/A'}")
except ValueError as e:
    print(f"Napaka pri parsiranju JSON: {e}")
except Exception as e:
    print(f"Nepričakovana napaka: {e}")