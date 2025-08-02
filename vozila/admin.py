from django.contrib import admin
from .models import Znamka, CarModel, TipVozila, Ilustracija, VoziloPodrobnosti, LokacijaOpis 

@admin.register(LokacijaOpis)
class LokacijaOpisAdmin(admin.ModelAdmin):
    list_display = ('opis', 'je_vin_lokacija', 'je_obd_lokacija') 
    list_filter = ('je_vin_lokacija', 'je_obd_lokacija') 
    search_fields = ('opis',)

@admin.register(Znamka)
class ZnamkaAdmin(admin.ModelAdmin):
    list_display = ('ime',)
    search_fields = ('ime',)
    ordering = ('ime',)

@admin.register(TipVozila)
class TipVozilaAdmin(admin.ModelAdmin):
    list_display = ('ime',)
    search_fields = ('ime',)

@admin.register(Ilustracija)
class IlustracijaAdmin(admin.ModelAdmin):
    list_display = ('opis', 'slika', 'je_vin_ilustracija', 'je_obd_ilustracija') 
    list_filter = ('je_vin_ilustracija', 'je_obd_ilustracija') 
    search_fields = ('opis',)

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('znamka', 'ime', 'generacija', 'leto_izdelave', 'tip_vozila')
    list_filter = ('znamka', 'tip_vozila', 'leto_izdelave')
    search_fields = ('ime', 'znamka__ime', 'generacija')
    ordering = ('znamka__ime', 'ime', '-leto_izdelave')

@admin.register(VoziloPodrobnosti)
class VoziloPodrobnostiAdmin(admin.ModelAdmin):
    list_display = (
        'car_model_display',
        'leto_od',
        'leto_do',
        'lokacija_vin_opis',
        'lokacija_obd_opis',
        'ilustracija_vin',
        'ilustracija_obd'
    )
    list_filter = (
        'car_model__znamka',
        'car_model__tip_vozila',
        'lokacija_vin_opis',
        'lokacija_obd_opis'
    )
    search_fields = (
        'car_model__znamka__ime',
        'car_model__ime',
        'lokacija_vin_opis__opis',
        'lokacija_obd_opis__opis',
        'opombe'
    )
    raw_id_fields = ('car_model',) 
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "lokacija_vin_opis":
            kwargs["queryset"] = LokacijaOpis.objects.filter(je_vin_lokacija=True).order_by('-opis')
        elif db_field.name == "lokacija_obd_opis":
            kwargs["queryset"] = LokacijaOpis.objects.filter(je_obd_lokacija=True).order_by('-opis')
        elif db_field.name == "ilustracija_vin":
            kwargs["queryset"] = Ilustracija.objects.filter(je_vin_ilustracija=True).order_by('opis')
        elif db_field.name == "ilustracija_obd":
            kwargs["queryset"] = Ilustracija.objects.filter(je_obd_ilustracija=True).order_by('opis')
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def car_model_display(self, obj):
        return f"{obj.car_model.znamka.ime} {obj.car_model.ime}"
    car_model_display.short_description = 'Model vozila'