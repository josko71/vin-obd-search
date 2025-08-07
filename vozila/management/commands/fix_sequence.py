from django.core.management.base import BaseCommand
from django.db import connection
from vozila.models import CarModel

class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT setval(pg_get_serial_sequence('"vozila_carmodel"','id'), 
                COALESCE((SELECT MAX(id) FROM "vozila_carmodel"), 1), false);
            """)
        self.stdout.write("Zaporedje ID-jev za CarModel popravljeno")

# V isti datoteki dodajte
from vozila.models import LokacijaOpis, Ilustracija

def reset_sequence(model):
    with connection.cursor() as cursor:
        table = model._meta.db_table
        cursor.execute(f"""
            SELECT setval(pg_get_serial_sequence('"{table}"','id'), 
            COALESCE((SELECT MAX(id) FROM "{table}"), 1), false);
        """)
