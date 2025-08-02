from django.shortcuts import render
from django.http import JsonResponse
from .models import CarModel, Znamka, TipVozila, VoziloPodrobnosti, Ilustracija, LokacijaOpis # Dodajte LokacijaOpis
from django.db.models import Q

def iskanje_vozil(request):
    # Pridobi vse podatke iz GET zahtevka
    znamka_id = request.GET.get('znamka')
    tip_vozila_id = request.GET.get('tip_vozila')
    model_id = request.GET.get('model')
    leto_od_query = request.GET.get('leto_od')
    leto_do_query = request.GET.get('leto_do')
    vin_lokacija_opis_query = request.GET.get('vin_lokacija_opis_query')
    obd_lokacija_opis_query = request.GET.get('obd_lokacija_opis_query')

    # Nastavi začetni queryset
    results = VoziloPodrobnosti.objects.all()

    # Ustvarimo Q objekt za združevanje filtrov
    query_conditions = Q()

    # Dodaj filter za znamko, če je izbrana
    if znamka_id:
        query_conditions &= Q(car_model__znamka__id=znamka_id)
    
    # Dodaj filter za tip vozila, če je izbran
    if tip_vozila_id:
        query_conditions &= Q(car_model__tip_vozila__id=tip_vozila_id)
    
    # Dodaj filter za model, če je izbran
    if model_id:
        query_conditions &= Q(car_model__id=model_id)
    
    # Dodaj filter za leto izdelave "od"
    if leto_od_query:
        try:
            leto_od_query = int(leto_od_query)
            # Preverjamo, ali je leto_od vozila manjše ali enako iskanemu letu_od
            # IN (leto_do vozila večje ali enako iskanemu letu_od ALI leto_do je null)
            query_conditions &= Q(leto_od__lte=leto_od_query) & \
                                (Q(leto_do__gte=leto_od_query) | Q(leto_do__isnull=True))
        except ValueError:
            pass # Ignoriraj neveljaven vnos

    # Dodaj filter za leto izdelave "do"
    if leto_do_query:
        try:
            leto_do_query = int(leto_do_query)
            # Preverjamo, ali je leto_od vozila manjše ali enako iskanemu letu_do
            query_conditions &= Q(leto_od__lte=leto_do_query)
        except ValueError:
            pass # Ignoriraj neveljaven vnos

    # Združi pogoje za opis lokacije VIN ali OBD z OR, če sta vnesena
    opis_location_query_conditions = Q()
    if vin_lokacija_opis_query:
        # POPRAVEK: Uporabite '__opis__icontains' za iskanje v opisu LokacijaOpis
        opis_location_query_conditions |= Q(lokacija_vin_opis__opis__icontains=vin_lokacija_opis_query)
    if obd_lokacija_opis_query:
        # POPRAVEK: Uporabite '__opis__icontains' za iskanje v opisu LokacijaOpis
        opis_location_query_conditions |= Q(lokacija_obd_opis__opis__icontains=obd_lokacija_opis_query)
    
    # Dodaj pogoje za opis lokacije k ostalim pogojem, samo če je kateri koli vnesen
    if vin_lokacija_opis_query or obd_lokacija_opis_query:
        query_conditions &= opis_location_query_conditions

    # Uporabi zbrane filtre na querysetu
    # Uporabimo select_related za učinkovito pridobivanje povezanih objektov
    # Uporabimo distinct(), da preprečimo podvojene rezultate
    results = results.filter(query_conditions).select_related(
        'car_model__znamka', 
        'car_model__tip_vozila', 
        'ilustracija_vin', 
        'ilustracija_obd',
        'lokacija_vin_opis', # Dodajte za učinkovit dostop do opisa
        'lokacija_obd_opis'  # Dodajte za učinkovit dostop do opisa
    ).distinct()

    # Pridobi podatke za dropdowne
    popularne_znamke = Znamka.objects.filter(je_popularna=True).order_by('ime')
    ostale_znamke = Znamka.objects.filter(je_popularna=False).order_by('ime')
    all_znamke = Znamka.objects.all().order_by('ime')
    all_tipi_vozil = TipVozila.objects.all().order_by('ime')

    # Pripravi znamke po tipu za JavaScript (json_script)
    znamke_po_tipu = {}
    for tip in TipVozila.objects.all():
        # Pridobimo ID-je znamk, ki so dejansko povezane s tem tipom vozila
        znamke_ids = CarModel.objects.filter(tip_vozila=tip).values_list('znamka_id', flat=True).distinct()
        znamke_po_tipu[str(tip.id)] = [str(z_id) for z_id in znamke_ids]

    context = {
        'results': results,
        'popularne_znamke_data': list(popularne_znamke.values('id', 'ime')),
        'ostale_znamke_data': list(ostale_znamke.values('id', 'ime')),
        'znamke_po_tipu': znamke_po_tipu,
        'all_znamke_data': list(all_znamke.values('id', 'ime')),
        'all_tipi_vozil': list(all_tipi_vozil.values('id', 'ime')), 
        # Za ohranjanje izbire v obrazcu
        'znamka_select': znamka_id,
        'tip_vozila_select': tip_vozila_id,
        'model_select': model_id,
        'leto_od': leto_od_query,
        'leto_do': leto_do_query,
        'vin_lokacija_opis_query': vin_lokacija_opis_query,
        'obd_lokacija_opis_query': obd_lokacija_opis_query,
    }

    return render(request, 'vozila/iskanje_vozil.html', context)


# Funkcija get_models_ajax ostane enaka, kot je bila predhodno popravljena
# in se uporablja za AJAX klice iz JavaScripta
def get_models_ajax(request):
    znamka_id = request.GET.get('znamka_id')
    tip_vozila_id = request.GET.get('tip_vozila_id')

    models = CarModel.objects.all()

    if znamka_id:
        models = models.filter(znamka__id=znamka_id)
    if tip_vozila_id:
        models = models.filter(tip_vozila__id=tip_vozila_id)

    # Vrnemo samo ID in ime modela
    data = list(models.values('id', 'ime').order_by('ime').distinct())
    
     # Dodajte logging za lažje razhroščevanje
    print(f"DEBUG: get_models_ajax - Znamka ID: {znamka_id}, Tip Vozila ID: {tip_vozila_id}")
    print(f"DEBUG: get_models_ajax - Število vrnjenih modelov: {len(data)}")
    print(f"DEBUG: get_models_ajax - Prvih 5 modelov: {data[:5]}")
    
    return JsonResponse(data, safe=False)