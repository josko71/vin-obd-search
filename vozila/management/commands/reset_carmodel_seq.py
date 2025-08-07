from django.core.management.base import BaseCommand
from django.db import connection
from vozila.models import CarModel

class Command(BaseCommand):
    help = 'Popravi zaporedje ID-jev za CarModel in zapolni vrzeli'

    def handle(self, *args, **options):
        # 1. Pridobimo trenutno stanje
        ids = list(CarModel.objects.order_by('id').values_list('id', flat=True))
        missing = sorted(set(range(1, max(ids)+1) - set(ids))
        
        self.stdout.write(f"Manjkajoči ID-ji: {len(missing)}")
        
        # 2. Popravimo sekvenco (PostgreSQL)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT setval(pg_get_serial_sequence('"vozila_carmodel"','id'), 
                COALESCE((SELECT MAX(id) FROM "vozila_carmodel"), 1), true);
            """)
        
        self.stdout.write(self.style.SUCCESS('✔ Sekvenca popravljena'))
        
        # 3. Opcijsko: Zapolnitev vrzeli z začasnimi zapisi
        if len(missing) > 1000:  # Samo če je veliko vrzeli
            self.stdout.write("Začasno zapolnjevanje vrzeli...")
            from vozila.models import Znamka
            znamka = Znamka.objects.first()
            
            temp_models = [
                CarModel(
                    znamka=znamka,
                    ime=f"temp_{i}",
                    generacija="TMP"
                )
                for i in missing[:1000]  # Omejimo na 1000 zapisov
            ]
            CarModel.objects.bulk_create(temp_models, batch_size=500)
            
            self.stdout.write(f"Ustvarjenih {len(temp_models)} začasnih zapisov")
