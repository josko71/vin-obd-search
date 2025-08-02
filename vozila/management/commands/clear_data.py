# vozila/management/commands/clear_data.py
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from vozila.models import VoziloPodrobnosti, Ilustracija, LokacijaOpis, CarModel, Znamka, TipVozila

class Command(BaseCommand):
    help = 'Clears all existing data from specified Django models in the correct order and resets IDs.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("WARNING: This command will DELETE ALL data from VoziloPodrobnosti, Ilustracija, LokacijaOpis, CarModel, Znamka, and TipVozila, AND RESET THEIR AUTO_INCREMENT IDs."))
        confirm = input("Are you sure you want to proceed? Type 'yes' to confirm: ")

        if confirm.lower() == 'yes':
            with transaction.atomic():
                self.stdout.write(self.style.HTTP_INFO("Clearing data and resetting IDs..."))

                # Pomembno: TRUNCATE v pravilnem vrstnem redu, da se izognete napakam tujih ključev
                # Najprej podrejene tabele, nato nadrejene
                tables_to_truncate = [
                    VoziloPodrobnosti._meta.db_table,
                    Ilustracija._meta.db_table, # Če Ilustracija ni child VoziloPodrobnosti, lahko pride prej
                    LokacijaOpis._meta.db_table, # Če LokacijaOpis ni child VoziloPodrobnosti, lahko pride prej
                    CarModel._meta.db_table,
                    Znamka._meta.db_table,
                    TipVozila._meta.db_table,
                ]

                # Preverite, ali je uporabnik MySQL/MariaDB
                # Za SQLite bo morda potreben drugačen pristop (npr. DROP TABLE in potem migrate)
                # Za MariaDB/MySQL je TRUNCATE TABLE ukaz primeren
                db_engine = connection.settings_dict['ENGINE']
                if 'mysql' in db_engine or 'mariadb' in db_engine:
                    # Onemogoči preverjanje tujih ključev za TRUNCATE, če so relacije med tabelami, ki se truncajo
                    # To je nujno, če truncate-amo več tabel, ki so med seboj povezane
                    cursor = connection.cursor()
                    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
                    try:
                        for table_name in tables_to_truncate:
                            self.stdout.write(f"Truncating table {table_name}...")
                            cursor.execute(f"TRUNCATE TABLE {table_name};")
                            self.stdout.write(self.style.SUCCESS(f"Table {table_name} truncated."))
                    finally:
                        # Vedno ponovno omogoči preverjanje tujih ključev
                        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
                        cursor.close()
                else:
                    self.stdout.write(self.style.WARNING(f"Database engine '{db_engine}' not explicitly supported for TRUNCATE. Using Django's ORM delete(). IDs might not reset."))
                    # Nadomestna rešitev za druge baze, če TRUNCATE ne deluje ali ni zaželen
                    VoziloPodrobnosti.objects.all().delete()
                    Ilustracija.objects.all().delete()
                    LokacijaOpis.objects.all().delete()
                    CarModel.objects.all().delete()
                    Znamka.objects.all().delete()
                    TipVozila.objects.all().delete()


            self.stdout.write(self.style.SUCCESS("All specified data cleared and IDs reset successfully."))
        else:
            self.stdout.write(self.style.ERROR("Data clearing cancelled."))