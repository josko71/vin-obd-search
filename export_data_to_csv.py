import os
import csv
import django
from django.conf import settings

# Nastavite Django okolje
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avto_vin_obd_projekt.settings')
django.setup()

from vozila.models import LokacijaOpis, Ilustracija, VoziloPodrobnosti

def export_model_to_csv(model, file_path, field_names):
    """
    Izvozi podatke iz modela v CSV datoteko.
    Pravilno obravnava ID-je tujih ključev.
    """
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(field_names)
        
        for obj in model.objects.all():
            row = []
            for field in field_names:
                # Preverimo, ali je polje tuji ključ (po konvenciji se konča z '_id')
                if field.endswith('_id'):
                    # Odstranimo '_id' in dobimo ime relacijskega polja
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
        ['id', 'opis', 'je_vin_lokacija', 'je_obd_lokacija']
    )
    print("Uspešno izvoženo LokacijaOpis.")

    # Izvoz Ilustracija
    export_model_to_csv(
        Ilustracija,
        os.path.join(csv_dir, 'ilustracije.csv'),
        ['id', 'carmodel_id', 'ime_slike']
    )
    print("Uspešno izvoženo Ilustracija.")

    # Izvoz VoziloPodrobnosti
    export_model_to_csv(
        VoziloPodrobnosti,
        os.path.join(csv_dir, 'vozilopodrobnosti.csv'),
        ['id', 'carmodel_id', 'opis', 'lokacija_opisa_id', 'vrednost']
    )
    print("Uspešno izvoženo VoziloPodrobnosti.")

    print("Izvoz podatkov zaključen.")