import os
import csv
import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from django.db.models import F

from vozila.models import LokacijaOpis, Znamka, TipVozila, CarModel, Ilustracija, VoziloPodrobnosti

class Command(BaseCommand):
    help = 'Uvozi podatke iz CSV datotek v bazo podatkov Django.'

    DEFAULT_CSV_DIR = 'data_csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Pot do mape, ki vsebuje CSV datoteke (relativno na manage.py ali absolutna).',
            default=self.DEFAULT_CSV_DIR
        )
        parser.add_argument(
            '--models',
            nargs='+',  # Sprejme enega ali več argumentov
            help='Seznam modelov, ki jih je treba uvoziti (npr. --models CarModel Ilustracija). Če ni navedeno, uvozi vse.',
            choices=[
                'lokacijaopis',
                'znamke',
                'tipivozila',
                'carmodels',
                'ilustracije',
                'vozilopodrobnosti'
            ]
        )

    # Funkcija za čiščenje nizov
    def clean_string(self, text):
        if text is None:
            return None
        cleaned_text = text.replace('\xa0', ' ').replace('\u202F', ' ').replace('\u00A0', ' ')
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text.strip()

    def handle(self, *args, **options):
        csv_dir_arg = options['path']
        models_to_import = options['models']
        if models_to_import:
            models_to_import = [m.lower() for m in models_to_import]
        
        if not os.path.isabs(csv_dir_arg):
            csv_dir = os.path.join(settings.BASE_DIR, csv_dir_arg)
        else:
            csv_dir = csv_dir_arg

        self.stdout.write(f"Začenjam uvoz podatkov iz {csv_dir}...")
        self.stdout.write("-" * 30)

        # --- Uvoz LokacijaOpis ---
        if not models_to_import or 'lokacijaopis' in models_to_import:
            lokacija_opis_csv_path = os.path.join(csv_dir, 'lokacijaopis.csv')
            self.stdout.write(f"Uvažam LokacijaOpis iz: {lokacija_opis_csv_path}")
            imported_lokacije_count = 0
            try:
                with open(lokacija_opis_csv_path, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file, delimiter=';')
                    with transaction.atomic():
                        for row in reader:
                            try:
                                required_fields = ['id', 'opis']
                                if not all(field in row for field in required_fields):
                                    self.stderr.write(self.style.ERROR(f"Vrstica manjka zahtevano polje ali je napačno ime glave v lokacijaopis.csv: {row}. Preskakujem."))
                                    continue

                                lokacija_id = int(row['id'])
                                lokacija_opis = self.clean_string(row['opis'])

                                LokacijaOpis.objects.update_or_create(
                                    id=lokacija_id,
                                    defaults={'opis': lokacija_opis}
                                )
                                imported_lokacije_count += 1
                            except Exception as e:
                                self.stderr.write(self.style.ERROR(f"Napaka pri uvozu LokacijaOpis '{row.get('opis', 'N/A')}': {e}. Preskakujem vrstico."))
                self.stdout.write(self.style.SUCCESS(f"Uspešno uvoženih/posodobljenih LokacijaOpis: {imported_lokacije_count}"))
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"Opozorilo: Datoteka {lokacija_opis_csv_path} ni najdena. Preskakujem uvoz lokacij opisa."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Kritična napaka pri branju lokacijaopis.csv: {e}"))
            self.stdout.write("-" * 30)

        # --- Uvoz Znamka ---
        if not models_to_import or 'znamke' in models_to_import:
            znamke_csv_path = os.path.join(csv_dir, 'znamke.csv')
            self.stdout.write(f"Uvažam Znamke iz: {znamke_csv_path}")
            imported_znamke_count = 0
            try:
                with open(znamke_csv_path, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file, delimiter=';')
                    with transaction.atomic():
                        for row in reader:
                            try:
                                if 'ime' not in row:
                                    self.stderr.write(self.style.ERROR(f"Vrstica manjka polje 'ime' v znamke.csv: {row}. Preskakujem."))
                                    continue

                                znamka_ime = self.clean_string(row['ime'])
                                znamka, created = Znamka.objects.get_or_create(ime=znamka_ime)
                                if created:
                                    imported_znamke_count += 1
                            except Exception as e:
                                self.stderr.write(self.style.ERROR(f"Napaka pri uvozu Znamke '{row.get('ime', 'N/A')}': {e}. Preskakujem vrstico."))
                self.stdout.write(self.style.SUCCESS(f"Uspešno uvoženih/posodobljenih Znamk: {imported_znamke_count}"))
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"Opozorilo: Datoteka {znamke_csv_path} ni najdena. Preskakujem uvoz znamk."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Kritična napaka pri branju znamke.csv: {e}"))
            self.stdout.write("-" * 30)

        # --- Uvoz TipVozila ---
        if not models_to_import or 'tipivozila' in models_to_import:
            tipivozila_csv_path = os.path.join(csv_dir, 'tipivozila.csv')
            self.stdout.write(f"Uvažam Tipe Vozil iz: {tipivozila_csv_path}")
            imported_tipi_count = 0
            try:
                with open(tipivozila_csv_path, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file, delimiter=';')
                    with transaction.atomic():
                        for row in reader:
                            try:
                                if 'ime' not in row:
                                    self.stderr.write(self.style.ERROR(f"Vrstica manjka polje 'ime' v tipivozila.csv: {row}. Preskakujem."))
                                    continue

                                tip_ime = self.clean_string(row['ime'])
                                tip_vozila, created = TipVozila.objects.get_or_create(ime=tip_ime)
                                if created:
                                    imported_tipi_count += 1
                            except Exception as e:
                                self.stderr.write(self.style.ERROR(f"Napaka pri uvozu TipVozila '{row.get('ime', 'N/A')}': {e}. Preskakujem vrstico."))
                self.stdout.write(self.style.SUCCESS(f"Uspešno uvoženih/posodobljenih Tipov Vozil: {imported_tipi_count}"))
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"Opozorilo: Datoteka {tipivozila_csv_path} ni najdena. Preskakujem uvoz tipov vozil."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Kritična napaka pri branju tipivozila.csv: {e}"))
            self.stdout.write("-" * 30)

        # --- Uvoz CarModel ---
        if not models_to_import or 'carmodels' in models_to_import:
            carmodels_csv_path = os.path.join(csv_dir, 'carmodels.csv')
            self.stdout.write(f"Uvažam CarModele iz: {carmodels_csv_path}")
            imported_carmodels_count = 0

            self.stdout.write("Nalaganje predpomnilnika znamk in tipov vozil...")
            znamke_cache = {self.clean_string(z.ime).lower(): z for z in Znamka.objects.all()}
            tipi_vozila_cache = {self.clean_string(t.ime).lower(): t for t in TipVozila.objects.all()}
            self.stdout.write("Predpomnilnik naložen.")

            try:
                with open(carmodels_csv_path, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file, delimiter=';')
                    
                    for row_num, row in enumerate(reader, 2):
                        try:
                            required_fields = ['id', 'ime', 'znamka_ime', 'tip_vozila_ime']
                            if not all(field in row for field in required_fields):
                                self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: Manjka zahtevano polje ali je napačno ime glave v carmodels.csv: {row}. Preskakujem."))
                                continue

                            model_id = int(row['id'])
                            model_ime = self.clean_string(row['ime'])
                            znamka_ime_csv = self.clean_string(row['znamka_ime'])
                            tip_vozila_ime_csv = self.clean_string(row['tip_vozila_ime'])

                            znamka = znamke_cache.get(znamka_ime_csv.lower())
                            tip_vozila = tipi_vozila_cache.get(tip_vozila_ime_csv.lower())

                            if not znamka:
                                self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: Znamka '{znamka_ime_csv}' ne obstaja v bazi. Preskakujem CarModel vrstico."))
                                continue
                            if not tip_vozila:
                                self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: Tip vozila '{tip_vozila_ime_csv}' ne obstaja v bazi. Preskakujem CarModel vrstico."))
                                continue
                            
                            with transaction.atomic():
                                carmodel, created = CarModel.objects.update_or_create(
                                    id=model_id,
                                    defaults={
                                        'znamka': znamka,
                                        'ime': model_ime,
                                        'generacija': self.clean_string(row.get('generacija', '')) or None,
                                        'leto_izdelave': int(row['leto_izdelave']) if row.get('leto_izdelave', '').strip() else None,
                                        'tip_vozila': tip_vozila,
                                    }
                                )
                                if created:
                                    imported_carmodels_count += 1
                                # Povežemo tudi ilustracije in podrobnosti, ki so že v bazi
                                # To zagotavlja, da so povezave z novimi carmodeli pravilne
                                # Ilustracija.objects.filter(id__in=...).update(carmodel=carmodel)
                                # VoziloPodrobnosti.objects.filter(id__in=...).update(carmodel=carmodel)

                        except ValueError as ve:
                            self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: Napaka pri pretvorbi podatkov (npr. ID ali Leto izdelave): {ve}. Podatki: {row}. Preskakujem CarModel vrstico."))
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: Nepričakovana napaka pri uvozu CarModel '{model_ime if 'model_ime' in locals() else 'N/A'}': {e}. Preskakujem CarModel vrstico."))

            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"Opozorilo: Datoteka {carmodels_csv_path} ni najdena. Preskakujem uvoz CarModelov."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Kritična napaka pri branju carmodels.csv: {e}"))
            self.stdout.write(self.style.SUCCESS(f"Uspešno uvoženih/posodobljenih CarModelov: {imported_carmodels_count}"))
            self.stdout.write("-" * 30)

        # --- Uvoz Ilustracija ---
        if not models_to_import or 'ilustracije' in models_to_import:
            ilustracije_csv_path = os.path.join(csv_dir, 'ilustracije.csv')
            self.stdout.write(f"Uvažam Ilustracije iz: {ilustracije_csv_path}")
            imported_ilustracije_count = 0
            try:
                with open(ilustracije_csv_path, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file, delimiter=';')
                    for row_num, row in enumerate(reader, 2):
                        try:
                            required_fields = ['id', 'carmodel_id', 'ime_slike']
                            if not all(field in row for field in required_fields):
                                self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: Manjka zahtevano polje ali je napačno ime glave v ilustracije.csv: {row}. Preskakujem."))
                                continue

                            ilustracija_id_str = row.get('id', '').strip()
                            carmodel_id_str = row.get('carmodel_id', '').strip()

                            if not ilustracija_id_str or not carmodel_id_str:
                                self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: ID ali carmodel_id sta prazna. Preskakujem vrstico."))
                                continue

                            ilustracija_id = int(ilustracija_id_str)
                            carmodel_id = int(carmodel_id_str)
                            ime_slike = self.clean_string(row.get('ime_slike', ''))

                            try:
                                carmodel = CarModel.objects.get(id=carmodel_id)
                            except CarModel.DoesNotExist:
                                self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: CarModel z ID {carmodel_id} za ilustracijo '{ime_slike}' ne obstaja. Preskakujem."))
                                continue
                            
                            with transaction.atomic():
                                ilustracija, created = Ilustracija.objects.update_or_create(
                                    id=ilustracija_id,
                                    defaults={
                                        'carmodel': carmodel,
                                        'ime_slike': ime_slike
                                    }
                                )
                                if created:
                                    imported_ilustracije_count += 1
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: Napaka pri uvozu Ilustracije '{row.get('ime_slike', 'N/A')}': {e}. Preskakujem vrstico."))
                self.stdout.write(self.style.SUCCESS(f"Uspešno uvoženih/posodobljenih Ilustracij: {imported_ilustracije_count}"))
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"Opozorilo: Datoteka {ilustracije_csv_path} ni najdena. Preskakujem uvoz ilustracij."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Kritična napaka pri branju ilustracije.csv: {e}"))
            self.stdout.write("-" * 30)

        # --- Uvoz VoziloPodrobnosti ---
        if not models_to_import or 'vozilopodrobnosti' in models_to_import:
            vozilopodrobnosti_csv_path = os.path.join(csv_dir, 'vozilopodrobnosti.csv')
            self.stdout.write(f"Uvažam VoziloPodrobnosti iz: {vozilopodrobnosti_csv_path}")
            imported_podrobnosti_count = 0
            try:
                with open(vozilopodrobnosti_csv_path, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file, delimiter=';')
                    for row_num, row in enumerate(reader, 2):
                        try:
                            required_fields = ['id', 'carmodel_id', 'opis', 'lokacija_opisa_id', 'vrednost']
                            if not all(field in row for field in required_fields):
                                self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: Manjka zahtevano polje ali je napačno ime glave v vozilopodrobnosti.csv: {row}. Preskakujem."))
                                continue

                            podrobnost_id_str = row.get('id', '').strip()
                            carmodel_id_str = row.get('carmodel_id', '').strip()
                            lokacija_opisa_id_str = row.get('lokacija_opisa_id', '').strip()

                            if not podrobnost_id_str or not carmodel_id_str or not lokacija_opisa_id_str:
                                self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: ID, carmodel_id ali lokacija_opisa_id je prazen. Preskakujem vrstico."))
                                continue
                            
                            podrobnost_id = int(podrobnost_id_str)
                            carmodel_id = int(carmodel_id_str)
                            lokacija_opisa_id = int(lokacija_opisa_id_str)
                            opis = self.clean_string(row.get('opis', ''))
                            vrednost = self.clean_string(row.get('vrednost', '')) or None

                            try:
                                carmodel = CarModel.objects.get(id=carmodel_id)
                            except CarModel.DoesNotExist:
                                self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: CarModel z ID {carmodel_id} za podrobnost '{opis}' ne obstaja. Preskakujem."))
                                continue

                            try:
                                lokacija_opisa = LokacijaOpis.objects.get(id=lokacija_opisa_id)
                            except LokacijaOpis.DoesNotExist:
                                self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: LokacijaOpis z ID {lokacija_opisa_id} za podrobnost '{opis}' ne obstaja. Preskakujem."))
                                continue
                            
                            with transaction.atomic():
                                podrobnost, created = VoziloPodrobnosti.objects.update_or_create(
                                    id=podrobnost_id,
                                    defaults={
                                        'carmodel': carmodel,
                                        'opis': opis,
                                        'lokacija_opisa': lokacija_opisa,
                                        'vrednost': vrednost
                                    }
                                )
                                if created:
                                    imported_podrobnosti_count += 1
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"Vrstica {row_num}: Napaka pri uvozu VoziloPodrobnosti '{row.get('opis', 'N/A')}': {e}. Preskakujem vrstico."))
                self.stdout.write(self.style.SUCCESS(f"Uspešno uvoženih/posodobljenih VoziloPodrobnosti: {imported_podrobnosti_count}"))
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"Opozorilo: Datoteka {vozilopodrobnosti_csv_path} ni najdena. Preskakujem uvoz podrobnosti vozil."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Kritična napaka pri branju vozilopodrobnosti.csv: {e}"))
            self.stdout.write("-" * 30)

        self.stdout.write(self.style.SUCCESS("Uvoz podatkov zaključen."))