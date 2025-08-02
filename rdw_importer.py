import os
import django
import time
from sodapy import Socrata
from datetime import datetime
from django.db import IntegrityError

# Nastavite Django okolje
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avto_vin_obd_projekt.settings')
django.setup()

# Uvozite modele, ki jih potrebujete. Preveri Ilustracija in VoziloPodrobnosti - is not accessed?!
from vozila.models import Znamka, CarModel, TipVozila, Ilustracija, VoziloPodrobnosti

# --- RDW API konfiguracija ---
RDW_DOMAIN = "opendata.rdw.nl"
RDW_DATASET_ID = "m9d7-ebf2" # Tukaj vnesite ID vašega RDW podatkovnega nabora (pozor: ta ID se lahko spremeni, preverite na RDW Open Data strani)
APP_TOKEN = "MF645CIo5eU72jWfRO5eZHGPH" # Tukaj vnesite svoj RDW API token (avtoPasdes12): https://opendata.rdw.nl/en/profile/edit/developer_settings

# --- Seznam znamk (ostane nespremenjen, je že dober) ---
BRANDS_TO_IMPORT = sorted(list(set([
    # Osebna vozila (50 najbolj priljubljenih v Sloveniji/Evropi)
    "VOLKSWAGEN", "RENAULT", "SKODA", "BMW", "AUDI", "PEUGEOT", "CITROEN", "TOYOTA",
    "DACIA", "FORD", "OPEL", "HYUNDAI", "KIA", "MERCEDES-BENZ", "SEAT", "SUZUKI",
    "MAZDA", "NISSAN", "VOLVO", "FIAT", "TESLA", "MG", "CUPRA", "ALFA ROMEO", "LAND ROVER",
    "JAGUAR", "MINI", "PORSCHE", "LEXUS", "HONDA", "MITSUBISHI", "CHEVROLET", "CHRYSLER",
    "JEEP", "SUBARU", "SMART", "LADA", "ABARTH", "DS", "GENESIS", "SSANGYONG",
    "ASTON MARTIN", "BENTLEY", "ROLLS-ROYCE", "FERRARI", "LAMBORGHINI", "MCLAREN",
    "BUGATTI", "LOTUS", "MASERATI", "ALPINE", "GEELY", "FORTHING",

    # Avtodomi / Bivalna vozila (30 najbolj priljubljenih)
    "ADRIA", "BURSTNER", "HYMER", "KNAUS", "MCLOUIS", "CHAUSSON", "MOBILVETTA",
    "BENIMAR", "ITINEO", "CARADO", "SUNLIGHT", "WEINSBERG", "DETHLEFFS", "RAPIDO",
    "PILOTE", "ELNAGH", "RIMOR", "CHALLENGER", "TRIGANO", "FONTE VERDE", "ERMATRA",
    "WESTFALIA", "POSSL", "DREAMER", "KARMEC", "FORSTER", "LAIKA", "FRANKIA",
    "NIESMANN+BISCHOFF", "MORELO", "MILLER",

    # Težka tovorna vozila (Tovornjaki in Cestni vlačilci)
    "DAF", "VOLVO TRUCKS", "SCANIA", "MAN", "MERCEDES-BENZ TRUCKS", "IVECO",
    "RENAULT TRUCKS", "SISU", "KAMA3", "TATRA", "FREIGHTLINER", "KENWORTH", "PETERBILT",
    "MACK", "INTERNATIONAL", "WESTERN STAR",

    # Motorna kolesa in skuterji (razširjeno na 50 najbolj priljubljenih, vključuje Tomos)
    "HONDA", "YAMAHA", "SUZUKI", "KAWASAKI", "KTM", "DUCATI", "BMW MOTORRAD",
    "TRIUMPH", "APRILIA", "MOTO GUZZI", "MV AGUSTA", "HUSQVARNA", "ROYAL ENFIELD",
    "HARLEY-DAVIDSON", "INDIAN", "VICTORY", "ENFIELD", "BENELLI", "CFMOTO", "ZONTES",
    "VESPA", "PIAGGIO", "SYM", "KYMCO", "LONCIN", "VOGE", "BSM", "NINEBOT",
    "SUPER SOCO", "ZERO", "ENERGICA", "CAFE RACER", "BUELL", "CAN-AM", "GASGAS",
    "BETA", "FANTIC", "SHERCO", "TRS", "VERTIGO", "TM", "MALAGUTI", "DERBI",
    "GILERA", "PEUGEOT MOTOCYCLES", "APRILIA SCOOTER", "KTM SCOOTER", "TOMOS",
    "LEXMOTO", "XIAOMI", "ENGWE", "PURE", "APOLLO", "BO", "JOYOR", "RICEEL",
    "AOVOPRO", "ISCOOTER", "TODIMART", "WOTTAN",

    # Traktorji
    "JOHN DEERE", "NEW HOLLAND", "MASSEY FERGUSON", "CASE IH", "FENDT", "KUBOTA",
    "VALTRA", "CLAAS", "SAME", "DEUTZ-FAHR", "JCB", "MCCORMICK", "ANTONIO CARRARO",
    "PASQUALI", "FERRARI", "GOLDONI", "ARBOS", "KIOTI", "ISEKI", "BCS", "AGRIA", "ZETOR",
    "BELARUS", "URSUS", "SOLIS", "LAMBORGHINI TRACTORS", "LANDINI", "HURLIMANN",
    "VERSATILE", "CHALLENGER", "KIROVETS", "DEERE & COMPANY", "FORD NEW HOLLAND",

    # Štirikolesniki (ATV/UTV)
    "POLARIS", "CFMOTO", "HONDA", "JOHN DEERE", "YAMAHA", "KAWASAKI", "KYMCO", "SUZUKI",
    "KUBOTA", "ARCTIC CAT", "CORVUS", "TUATARA", "BRP", "ALKE", "CAN-AM", "ACCESS",
    "AEON", "GOES", "KAYO", "LINHAI", "LONCIN", "ODES", "SEGWAY", "TGB", "TEXTRON",
    "HISUN", "STELS", "CANNONDALE", "KUBERG", "SUR-RON", "KAISHA"
])))


# --- Seznam tipov vozil (ostane nespremenjen, je že dober) ---
VEHICLE_TYPES_TO_IMPORT = [
    "Personenauto",     # Osebni avtomobili
    "Bedrijfsauto",     # Lahka/težka gospodarska vozila, kombiji
    "Motorfiets",       # Motorna kolesa
    "Bromfiets",        # Mopedi/Skuterji
    "Landbouwvoertuig", # Traktorji in kmetijski stroji
    "Aanhangwagen",     # Prikolice (splošno)
    "Speciaal voertuig", # Vozila s posebno namembnostjo (avtodomi so lahko tukaj)
]

# --- Funkcija za pridobivanje podatkov iz RDW API ---
def fetch_rdw_data(limit=1000, offset=0):
    client = Socrata(RDW_DOMAIN, APP_TOKEN, timeout=180) 
    
    # IZBOLJŠAVA TUKAJ: spremenili 'voertuigcategorie' v 'europese_voertuigcategorie'
    fields = "merk, handelsbenaming, datum_eerste_toelating, voertuigsoort, inrichting, europese_voertuigcategorie" 
    
    brands_filter_soql = ", ".join(f"'{brand}'" for brand in BRANDS_TO_IMPORT)
    types_filter_soql = ", ".join(f"'{v_type}'" for v_type in VEHICLE_TYPES_TO_IMPORT)

    # IZBOLJŠAVA TUKAJ: spremenili 'voertuigcategorie' v 'europese_voertuigcategorie'
    where_clause = (
        f"merk IN ({brands_filter_soql}) AND ("
        f"voertuigsoort IN ({types_filter_soql})"
        f" OR europese_voertuigcategorie IN ('N2', 'N3', 'O1', 'O2', 'O3', 'O4', 'L1', 'L3')"
        f" OR inrichting = 'CAMPER'" 
        f")"
    )
    
    print(f"DEBUG: Generirana WHERE klavzula: {where_clause}") 
    
    try:
        results = client.get(
            RDW_DATASET_ID,
            select=fields,
            limit=limit, 
            offset=offset,
            order="merk, handelsbenaming, datum_eerste_toelating",
            where=where_clause 
        )
        return results
    except Exception as e:
        print(f"Napaka pri pridobivanju podatkov iz RDW API: {e}")
        return None

# --- Funkcija za parsiranje generacije modela (ostane nespremenjena) ---
def parse_model_generation(model_name, body_description):
    model_name_upper = model_name.upper()
    roman_numerals = {"I":1, "II":2, "III":3, "IV":4, "V":5, "VI":6, "VII":7, "VIII":8, "IX":9, "X":10}
    for numeral, _ in roman_numerals.items():
        if f" {numeral}" in model_name_upper:
            return numeral
    
    return None 

# --- Glavna funkcija za uvoz podatkov ---
def import_rdw_data_to_django():
    print("Začenjam uvoz podatkov iz RDW v Django bazo...")
    
    total_records_to_fetch = 15000000 # TU SPREMENI KOLIKO VRSTIC PODATKOV ŽELIŠ UVOZITI
    batch_size = 50000 
    processed_count = 0
    
    znamke_cache = {}
    tipi_vozil_cache = {}
    seen_carmodels = set() 

    for znamka in Znamka.objects.all():
        znamke_cache[znamka.ime] = znamka
    for tip_vozila in TipVozila.objects.all():
        tipi_vozil_cache[tip_vozila.ime] = tip_vozila
    
    while processed_count < total_records_to_fetch:
        print(f"Pridobivam podatke: offset={processed_count}, limit={batch_size}...")
        records = fetch_rdw_data(limit=batch_size, offset=processed_count)
        
        if not records:
            print("Ni več zapisov za pridobivanje ali napaka pri API klicu. Končujem uvoz.")
            break

        records_in_batch = len(records)
        for record in records:
            merk = record.get('merk') 
            handelsbenaming = record.get('handelsbenaming') 
            datum_eerste_toelating = record.get('datum_eerste_toelating') 
            voertuigsoort = record.get('voertuigsoort') 
            inrichting = record.get('inrichting') 
            # IZBOLJŠAVA TUKAJ: pridobivamo 'europese_voertuigcategorie'
            europese_voertuigcategorie = record.get('europese_voertuigcategorie') 

            # Uporabi "najboljši" tip vozila, če je na voljo
            final_voertuigsoort = voertuigsoort
            if not final_voertuigsoort and europese_voertuigcategorie:
                # Mapiraj evropske kategorije na splošnejše slovenske/opisne, če ni direktnega voertuigsoort
                if europese_voertuigcategorie.startswith('N'):
                    final_voertuigsoort = "Bedrijfsauto (EuroCat N)"
                elif europese_voertuigcategorie.startswith('O'):
                    final_voertuigsoort = "Aanhangwagen (EuroCat O)"
                elif europese_voertuigcategorie.startswith('L'):
                    final_voertuigsoort = "Motorno kolo/Skuter (EuroCat L)"
            
            # Še vedno preveri, da imamo osnovne podatke
            if not (merk and handelsbenaming and datum_eerste_toelating and final_voertuigsoort):
                continue

            try:
                leto_izdelave = int(str(datum_eerste_toelating)[:4])
            except (ValueError, TypeError):
                leto_izdelave = None

            generacija = parse_model_generation(handelsbenaming, inrichting)

            # Preveri in ustvari TipVozila
            if final_voertuigsoort not in tipi_vozil_cache:
                try:
                    tip_vozila_obj, created_tip = TipVozila.objects.get_or_create(ime=final_voertuigsoort)
                    if created_tip:
                        print(f"  Ustvarjen nov tip vozila: {final_voertuigsoort}")
                    tipi_vozil_cache[final_voertuigsoort] = tip_vozila_obj
                except IntegrityError:
                    tip_vozila_obj = TipVozila.objects.get(ime=final_voertuigsoort)
                    tipi_vozil_cache[final_voertuigsoort] = tip_vozila_obj
            else:
                tip_vozila_obj = tipi_vozil_cache[final_voertuigsoort]

            # Preveri in ustvari Znamka
            if merk not in znamke_cache:
                try:
                    znamka_obj, created_brand = Znamka.objects.get_or_create(ime=merk)
                    if created_brand:
                        pass
                    znamke_cache[merk] = znamka_obj
                except IntegrityError:
                    znamka_obj = Znamka.objects.get(ime=merk)
                    znamke_cache[merk] = znamka_obj
            else:
                znamka_obj = znamke_cache[merk]

            # Poskusi ustvariti/dobiti CarModel
            model_key = (znamka_obj.ime, handelsbenaming, generacija, leto_izdelave, tip_vozila_obj.ime)
            
            try:
                carmodel_obj, created_model = CarModel.objects.get_or_create(
                    znamka=znamka_obj,
                    ime=handelsbenaming,
                    generacija=generacija,
                    leto_izdelave=leto_izdelave,
                    tip_vozila=tip_vozila_obj
                )
                if created_model:
                    pass
                seen_carmodels.add(model_key)
            except IntegrityError:
                try:
                    carmodel_obj = CarModel.objects.get(
                        znamka=znamka_obj,
                        ime=handelsbenaming,
                        generacija=generacija,
                        leto_izdelave=leto_izdelave,
                        tip_vozila=tip_vozila_obj
                    )
                    seen_carmodels.add(model_key)
                except CarModel.DoesNotExist:
                    print(f"  Napaka: Model '{merk} {handelsbenaming}' ni bil najden po IntegrityError.")
                except Exception as e_get:
                    print(f"  Napaka pri pridobivanju obstoječega modela '{merk} {handelsbenaming}': {e_get}")
            except Exception as e:
                print(f"  Napaka pri shranjevanju/pridobivanju modela '{merk} {handelsbenaming}': {e}")
                
        processed_count += records_in_batch
        print(f"  Obdelanih {records_in_batch} zapisov. Skupaj obdelanih: {processed_count}.")
        
        if records_in_batch < batch_size:
            print("Dosežen konec podatkov ali manj zapisov kot zahtevan limit. Končujem uvoz.")
            break
        
        time.sleep(0.1)

    print("\nUvoz podatkov zaključen.")
    print(f"Skupno število edinstvenih znamk v cache-u: {len(znamke_cache)}")
    print(f"Skupno število edinstvenih modelov obdelanih: {len(seen_carmodels)}")

if __name__ == "__main__":
    import_rdw_data_to_django()