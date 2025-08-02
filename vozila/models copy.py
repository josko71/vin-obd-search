from django.db import models

# ... (vaši obstoječi modeli CarModel, Znamka, TipVozila, VoziloPodrobnosti, Ilustracija) ...

class LokacijaOpis(models.Model):
    opis = models.CharField(max_length=255, unique=True, verbose_name="Opis lokacije")

    class Meta:
        verbose_name = "Opis lokacije"
        verbose_name_plural = "Opisi lokacij"
        ordering = ['opis'] # Za urejen prikaz v spustnem seznamu

    def __str__(self):
        return self.opis

class Znamka(models.Model):
    ime = models.CharField(max_length=100, unique=True)
    je_popularna = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Znamka vozila"
        verbose_name_plural = "Znamke vozil"

    def __str__(self):
        return self.ime

class TipVozila(models.Model):
    ime = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Tip vozila"
        verbose_name_plural = "Tipi vozil"

    def __str__(self):
        return self.ime

class CarModel(models.Model):
    znamka = models.ForeignKey(Znamka, on_delete=models.CASCADE, verbose_name="Znamka")
    ime = models.CharField(max_length=255, verbose_name="Ime modela")
    generacija = models.CharField(max_length=100, blank=True, null=True, verbose_name="Generacija (npr. Mk1, Mk2)")
    leto_izdelave = models.IntegerField(blank=True, null=True, verbose_name="Leto izdelave modela")
    tip_vozila = models.ForeignKey(TipVozila, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tip vozila")

    class Meta:
        verbose_name = "Model avtomobila"
        verbose_name_plural = "Modeli avtomobilov"
        unique_together = ('znamka', 'ime', 'generacija', 'leto_izdelave')
        ordering = ['znamka__ime', 'ime', 'leto_izdelave']


    def __str__(self):
        display_name = f"{self.znamka.ime} {self.ime}"
        if self.generacija:
            display_name += f" ({self.generacija})"
        if self.leto_izdelave:
            display_name += f" ({self.leto_izdelave})"
        if self.tip_vozila:
            display_name += f" [{self.tip_vozila.ime}]"
        return display_name


class Ilustracija(models.Model):
    slika = models.ImageField(upload_to='ilustracije/', verbose_name="Slika ilustracije")
    opis = models.CharField(max_length=255, blank=True, null=True, verbose_name="Opis ilustracije")

    class Meta:
        verbose_name = "Ilustracija lokacije"
        verbose_name_plural = "Ilustracije lokacij"

    def __str__(self):
        return self.opis or f"Ilustracija {self.id}"

# Ime modela je VoziloPodrobnosti, ne PodrobnostiVINOBD
class VoziloPodrobnosti(models.Model):
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, verbose_name="Model avtomobila")

    leto_od = models.IntegerField(blank=True, null=True, verbose_name="Leto izdelave od")
    leto_do = models.IntegerField(blank=True, null=True, verbose_name="Leto izdelave do")

     # SPREMENJENO: Uporaba ForeignKey na LokacijaOpis
    lokacija_vin_opis = models.ForeignKey(
        LokacijaOpis, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='vin_lokacije', 
        verbose_name="Lokacija VIN številke"
    )
    lokacija_obd_opis = models.ForeignKey(
        LokacijaOpis, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='obd_lokacije', 
        verbose_name="Lokacija OBD priklopa"
    )

    ilustracija_vin = models.ForeignKey(
        Ilustracija, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='vin_podrobnosti', verbose_name="Ilustracija VIN lokacije"
    )
  
    ilustracija_obd = models.ForeignKey(
        Ilustracija, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='obd_podrobnosti', verbose_name="Ilustracija OBD lokacije"
    )
    opombe = models.TextField(blank=True, null=True, verbose_name="Dodatne opombe")

    class Meta:
        verbose_name = "Podrobnosti vozila (VIN/OBD)"
        verbose_name_plural = "Podrobnosti vozil (VIN/OBD)"
        unique_together = ('car_model', 'leto_od', 'leto_do')
        ordering = ['car_model__znamka__ime', 'car_model__ime', 'leto_od']

    def __str__(self):
        model_str = f"{self.car_model.znamka.ime} {self.car_model.ime}"
        letnice_str = ""
        if self.leto_od and self.leto_do:
            letnice_str = f" ({self.leto_od}-{self.leto_do})"
        elif self.leto_od:
            letnice_str = f" ({self.leto_od}-)"
        elif self.leto_do:
            letnice_str = f" (-{self.leto_do})"

        vin_opis = self.lokacija_vin_opis.opis if self.lokacija_vin_opis else "N/A"
        obd_opis = self.lokacija_obd_opis.opis if self.lokacija_obd_opis else "N/A"

        return f"{model_str}{letnice_str} | VIN: {vin_opis} | OBD: {obd_opis}"