import requests
import pandas as pd
from collections import Counter

# --- Konfiguracija API-ja RDW ---
# Osnovni URL za podatke o vozilih
# RDW podatki o vozilih so dostopni na tem Socrata Open Data API endpointu.
# Dokumentacijo za Socrata API lahko najdete na https://dev.socrata.com/
BASE_URL = "https://opendata.rdw.nl/resource/mrdw-lpgl-tggj.json"

# --- Parametri API poizvedbe ---
# Uporabljamo Socrata Query Language (SoQL) za filtriranje in agregacijo.
# Omejimo na osebne avtomobile ('Personenauto') in pridobimo določeno število rezultatov.
# $limit: Omeji število vrnjenih zapisov.
# $where: Filtrira podatke po pogojih. Tukaj iščemo le 'Personenauto'.
# $select: Izbere določene stolpce. Želimo le 'merk' (znamko).
# $group: Agregira po znamki.
# $order: Razvrsti po številu pojavitev znamke.
# $q: Iskalni niz (ni vedno potreben, a lahko pomaga pri optimizaciji).
# Za podrobnosti o SoQL sintaksi glej https://dev.socrata.com/docs/queries/
params = {
    "$limit": 2000, # Pridobimo dovolj zapisov, da najdemo 20 najbolj pogostih
    "$where": "voertuigsoort = 'Personenauto'",
    "$select": "merk",
    # Pomembno: Socrata API ne omogoča neposrednega štetja in razvrščanja Top-N z enim samim $group/$select.
    # Zato bomo raje prenesli določeno število in štetje izvedli lokalno.
    # Lahko pa bi uporabili tudi "$group=merk&$select=merk,count(merk) AS count_merk&$order=count_merk DESC&$limit=20"
    # vendar je včasih enostavneje ročno obdelati z pandas, sploh če se API odziva počasi.
}

print("Povezujem se z RDW Open Data API-jem...")

try:
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status() # Sproži izjemo za HTTP napake (4xx ali 5xx)
    data = response.json()

    if not data:
        print("Ni najdenih podatkov za 'Personenauto'. Preverite API endpoint in parametre.")
    else:
        # Pretvorimo podatke v DataFrame za enostavnejšo obdelavo
        df = pd.DataFrame(data)

        # Odstranimo morebitne manjkajoče vrednosti v stolpcu 'merk'
        df = df.dropna(subset=['merk'])

        # Preštejemo pogostost posameznih znamk
        brand_counts = df['merk'].value_counts()

        # Izberemo 20 najbolj priljubljenih znamk
        top_20_brands = brand_counts.head(20)

        print("\n--- 20 najbolj priljubljenih avtomobilskih znamk (RDW podatki) ---")
        for brand, count in top_20_brands.items():
            print(f"- {brand}: {count} pojavitev")

except requests.exceptions.RequestException as e:
    print(f"Napaka pri povezovanju z API-jem: {e}")
except ValueError:
    print("Napaka pri dekodiranju JSON odgovora. Morda API ni vrnil veljavnega JSON-a.")
except Exception as e:
    print(f"Prišlo je do nepričakovane napake: {e}")