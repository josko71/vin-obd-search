from django.core.management.base import BaseCommand
from vozila.models import (LokacijaOpis, Znamka, TipVozila, 
                         CarModel, Ilustracija, VoziloPodrobnosti)
import random

class Command(BaseCommand):
    help = 'Preverjanje integritete modelov in baze'

    def handle(self, *args, **options):
        self.stdout.write("\n=== Začenjam testiranje modelov ===\n")
        
        # 1. Testiranje LokacijaOpis
        self.stdout.write("1. Testiranje LokacijaOpis...")
        lok1 = LokacijaOpis.objects.create(
            opis="Testna lokacija",
            je_vin_lokacija=True,
            je_obd_lokacija=False
        )
        self.stdout.write(f"Ustvarjen: {lok1}")
        
        # Preveri unique constraint
        try:
            LokacijaOpis.objects.create(opis="Testna lokacija")
            self.stdout.write(self.style.ERROR("Napaka: unique constraint ne deluje!"))
        except:
            self.stdout.write("✓ Unique constraint deluje")
        
        # 2. Testiranje Znamka
        self.stdout.write("\n2. Testiranje Znamka...")
        znamka = Znamka.objects.create(
            ime="TestnaZnamka",
            je_popularna=True
        )
        self.stdout.write(f"Ustvarjen: {znamka}")
        
        # Update test
        znamka.ime = "PosodobljenaZnamka"
        znamka.save()
        self.stdout.write(f"Posodobljen: {znamka}")
        
        # 3. Testiranje TipVozila
        self.stdout.write("\n3. Testiranje TipVozila...")
        tip = TipVozila.objects.create(ime="TestniTip")
        self.stdout.write(f"Ustvarjen: {tip}")
        
        # 4. Testiranje CarModel
        self.stdout.write("\n4. Testiranje CarModel...")
        model = CarModel.objects.create(
            znamka=znamka,
            ime="TestniModel",
            generacija="Mk1",
            leto_izdelave=2020,
            tip_vozila=tip
        )
        self.stdout.write(f"Ustvarjen: {model}")
        
        # Preveri unique_together
        try:
            CarModel.objects.create(
                znamka=znamka,
                ime="TestniModel",
                generacija="Mk1",
                leto_izdelave=2020
            )
            self.stdout.write(self.style.ERROR("Napaka: unique_together ne deluje!"))
        except:
            self.stdout.write("✓ Unique_together deluje")
        
        # 5. Testiranje Ilustracija
        self.stdout.write("\n5. Testiranje Ilustracija...")
        ilustracija = Ilustracija.objects.create(
            opis="Testna ilustracija",
            je_vin_ilustracija=True
        )
        self.stdout.write(f"Ustvarjen: {ilustracija}")
        
        # 6. Testiranje VoziloPodrobnosti
        self.stdout.write("\n6. Testiranje VoziloPodrobnosti...")
        podrobnosti = VoziloPodrobnosti.objects.create(
            car_model=model,
            leto_od=2018,
            leto_do=2022,
            lokacija_vin_opis=lok1,
            ilustracija_vin=ilustracija
        )
        self.stdout.write(f"Ustvarjen: {podrobnosti}")
        
        # Preveri unique_together
        try:
            VoziloPodrobnosti.objects.create(
                car_model=model,
                leto_od=2018,
                leto_do=2022
            )
            self.stdout.write(self.style.ERROR("Napaka: unique_together ne deluje!"))
        except:
            self.stdout.write("✓ Unique_together deluje")
        
        # 7. Preverjanje ID zaporedja
        self.stdout.write("\n7. Preverjanje ID zaporedja...")
        models_to_check = [LokacijaOpis, Znamka, TipVozila, CarModel, Ilustracija, VoziloPodrobnosti]
        
        for model in models_to_check:
            ids = list(model.objects.all().order_by('id').values_list('id', flat=True))
            if ids:
                expected = list(range(1, max(ids)+1))
                missing = sorted(set(expected) - set(ids))
                if missing:
                    self.stdout.write(self.style.WARNING(f"{model.__name__}: Manjkajoči ID-ji {missing}"))
                else:
                    self.stdout.write(f"{model.__name__}: ✓ ID zaporedje brez vrzeli")
            else:
                self.stdout.write(f"{model.__name__}: Ni zapisov")
        
        # 8. Brisanje testnih podatkov
        self.stdout.write("\n8. Čiščenje testnih podatkov...")
        VoziloPodrobnosti.objects.filter(car_model__znamka=znamka).delete()
        CarModel.objects.filter(znamka=znamka).delete()
        Ilustracija.objects.filter(opis__contains="Test").delete()
        TipVozila.objects.filter(ime__contains="Test").delete()
        Znamka.objects.filter(ime__contains="Test").delete()
        LokacijaOpis.objects.filter(opis__contains="Test").delete()

                
        self.stdout.write(self.style.SUCCESS("\n=== Vsi testi uspešno zaključeni ==="))

