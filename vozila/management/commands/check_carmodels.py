# vozila/management/commands/check_carmodels.py

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from vozila.models import CarModel

class Command(BaseCommand):
    help = 'Checks for corrupted CarModel entries in the database.'

    def handle(self, *args, **options):
        self.stdout.write("Začenjam preverjanje CarModel...")

        # 1. Poskusite najti prazen ali NULL ID
        try:
            # To bo ujelo primer praznega niza za ID
            corrupted_object = CarModel.objects.get(pk='')
            self.stdout.write(self.style.ERROR(f"Najden poškodovan objekt s praznim ID-jem! Poskušam ga izbrisati..."))
            corrupted_object.delete()
            self.stdout.write(self.style.SUCCESS("Poškodovan objekt uspešno izbrisan."))
            return
        except ObjectDoesNotExist:
            pass
        except ValueError:
            self.stdout.write(self.style.SUCCESS("Ni poškodovanega objekta z ID-jem, ki ni številka. Nadaljujem z preverjanjem..."))

        # 2. Preverite IDs, ki so manjši od prvega obstoječega
        self.stdout.write("Preverjam morebitne manjkajoče ali poškodovane ID-je...")

        first_model_pk = CarModel.objects.first().pk
        self.stdout.write(f"Prvi ID je: {first_model_pk}")

        # Poskusite pridobiti objekte z ID-ji manjšimi od prvega, da preverite, ali so bili izbrisani
        corrupted_candidates = CarModel.objects.filter(pk__lt=first_model_pk)
        if corrupted_candidates.exists():
            self.stdout.write(self.style.WARNING(f"Najdeni so potencialno poškodovani zapisi pred ID {first_model_pk}."))
            for obj in corrupted_candidates:
                try:
                    int(obj.pk)
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Najden je poškodovan objekt z ID-jem '{obj.pk}'."))
                    obj.delete()
                    self.stdout.write(self.style.SUCCESS("Poškodovan objekt uspešno izbrisan."))
        else:
            self.stdout.write(self.style.SUCCESS("Ni poškodovanih zapisov, ki bi jih bilo mogoče zaznati."))