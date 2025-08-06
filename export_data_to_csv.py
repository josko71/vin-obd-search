import os
import csv
import django
from django.conf import settings

# Nastavite Django okolje
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avto_vin_obd_projekt.settings')
django.setup()

from vozila.models import LokacijaOpis, Ilustracija, VoziloPodrobnosti, Znamka, TipVozila, CarModel

def export_model_to_csv(model, file_path, field_names, required_fields=[]):
    """
    Izvozi podatke iz modela v CSV datoteko.
    Preskoči vrstice, če manjkajo zahtevana polja.
    Pravilno obravnava ID-je tujih ključev.
    """
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(field_names)
        
        for obj in model.objects.all():
            is_valid = True
            
            # Preverimo, ali so vsa zahtevana polja prisotna
            for required_field in required_fields:
                if not getattr(obj, required_field, None):
                    is_valid = False
                    # print(f"Opozorilo: Preskakujem {model.__name__} (ID: {obj.id}), ker mu manjka polje '{required_field}'.")
                    break
            
            if not is_valid:
                continue

            row = []
            for field in field_names:
                if field.endswith('_id'):
                    related_field_name = field[:-3]
                    related_obj = getattr(obj, related_field_name, None)
                    row.append(getattr(related_obj, 'id', None))
                else:
                    row.append(getattr(obj, field, None))
            writer.writerow(row)

if __name__ == '__main__':
    csv_dir = os.path.join(settings.BASE_DIR, 'data_csv')
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    print("Začenjam izvoz podatkov v CSV datoteke...")

    # Izvoz LokacijaOpis
    export_model_to_csv(
        LokacijaOpis,
        os.path.join(csv_dir, 'lokacijaopis.csv'),
        ['id', 'opis', 'je_vin_lokacija', 'je_obd_lokacija'],
        required_fields=['id', 'opis']
    )
    print("Uspešno izvoženo LokacijaOpis.")
    
    # Izvoz Znamka
    export_model_to_csv(
        Znamka,
        os.path.join(csv_dir, 'znamke.csv'),
        ['id', 'ime'],
        required_fields=['id', 'ime']
    )
    print("Uspešno izvoženo Znamka.")
    
    # Izvoz TipVozila
    export_model_to_csv(
        TipVozila,
        os.path.join(csv_dir, 'tipivozila.csv'),
        ['id', 'ime'],
        required_fields=['id', 'ime']
    )
    print("Uspešno izvoženo TipVozila.")

    # Izvoz CarModel
    export_model_to_csv(
        CarModel,
        os.path.join(csv_dir, 'carmodels.csv'),
        ['id', 'znamka_id', 'ime', 'generacija', 'leto_izdelave', 'tip_vozila_id'],
        required_fields=['id', 'znamka', 'tip_vozila']
    )
    print("Uspešno izvoženo CarModel.")

    # Izvoz Ilustracija
    export_model_to_csv(
        Ilustracija,
        os.path.join(csv_dir, 'ilustracije.csv'),
        ['id', 'carmodel_id', 'ime_slike'],
        required_fields=['id', 'carmodel', 'ime_slike']
    )
    print("Uspešno izvoženo Ilustracija.")

    # Izvoz VoziloPodrobnosti
    export_model_to_csv(
        VoziloPodrobnosti,
        os.path.join(csv_dir, 'vozilopodrobnosti.csv'),
        ['id', 'carmodel_id', 'opis', 'lokacija_opisa_id', 'vrednost'],
        required_fields=['id', 'carmodel', 'lokacija_opisa', 'opis']
    )
    print("Uspešno izvoženo VoziloPodrobnosti.")

    print("Izvoz podatkov zaključen.")