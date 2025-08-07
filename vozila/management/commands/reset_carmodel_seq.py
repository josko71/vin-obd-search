from django.core.management.base import BaseCommand
from django.db import connection
from vozila.models import CarModel

class Command(BaseCommand):
    help = 'Popravi zaporedje ID-jev za CarModel in zapolni vrzeli'

    def handle(self, *args, **options):
        # 1. Pridobimo trenutno stanje
        ids = list(CarModel.objects.order_by('id').values_list('id', flat=True))
        if not ids:
            self.stdout.write(self.style.WARNING('Ni zapisov v bazi'))
            return
            
        max_id = max(ids)
        missing = sorted(set(range(1, max_id + 1)) - set(ids))
        
        self.stdout.write(f"Število zapisov: {len(ids)}")
        self.stdout.write(f"Zadnji ID: {max_id}")
        self.stdout.write(f"Manjkajoči ID-ji: {len(missing)}")
        
        # 2. Popravimo sekvenco (PostgreSQL)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT setval(pg_get_serial_sequence('"vozila_carmodel"','id'), 
                COALESCE((SELECT MAX(id) FROM "vozila_carmodel"), 1), true);
            """)
        
        self.stdout.write(self.style.SUCCESS('✔ Sekvenca popravljena'))
        
        # 3. Opcijsko: Zapolnitev vrzeli
        if len(missing) > 1000 and input('Želite zapolniti vrzeli? (da/ne): ') == 'da':
            from vozila.models import Znamka
            znamka = Znamka.objects.first()
            if not znamka:
                self.stdout.write(self.style.ERROR('Ni znamke za ustvarjanje testnih zapisov'))
                return
                
            temp_models = [
                CarModel(
                    znamka=znamka,
                    ime=f"temp_{i}",
                    generacija="TMP"
                )
                for i in missing[:1000]  # Omejimo na 1000 zapisov
            ]
            created = CarModel.objects.bulk_create(temp_models, batch_size=500)
            self.stdout.write(f"Ustvarjenih {len(created)} začasnih zapisov")