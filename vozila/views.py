from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import Znamka, TipVozila, CarModel, VoziloPodrobnosti, LokacijaOpis 

# Definirajte vse funkcije v eni datoteki brez podvajanja

def get_models_ajax(request):
    znamka_id = request.GET.get('znamka_id')
    tip_vozila_id = request.GET.get('tip_vozila_id')

    # Začnemo z VoziloPodrobnosti, da najdemo modele, ki imajo VIN ali OBD ilustracije
    # To bo bistveno zmanjšalo število poizvedb na bazo.
    relevant_details_queryset = VoziloPodrobnosti.objects.filter(
        Q(ilustracija_vin__isnull=False) | Q(ilustracija_obd__isnull=False)
    ).select_related('car_model__znamka', 'car_model__tip_vozila') # Prednaložimo povezane objekte

    # Dodatno filtriranje glede na znamko in tip vozila, če sta podana
    if znamka_id:
        relevant_details_queryset = relevant_details_queryset.filter(car_model__znamka_id=znamka_id)
    
    if tip_vozila_id:
        relevant_details_queryset = relevant_details_queryset.filter(car_model__tip_vozila_id=tip_vozila_id)

    # Zberemo edinstvene modele in njihove lastnosti (VIN/OBD)
    models_info = {} # Uporabimo slovar za edinstvenost in zbiranje podatkov

    for detail in relevant_details_queryset:
        model = detail.car_model
        model_id = model.id

        if model_id not in models_info:
            models_info[model_id] = {
                'id': model.id,
                'name': str(model),
                'has_vin': False,
                'has_obd': False
            }
        
        if detail.ilustracija_vin:
            models_info[model_id]['has_vin'] = True
        if detail.ilustracija_obd:
            models_info[model_id]['has_obd'] = True
    
    # Pretvori slovar v seznam in dodaj indikatorje v ime
    filtered_models_data = []
    for model_id, info in models_info.items():
        display_name = info['name']
        indicators = []
        if info['has_vin']:
            indicators.append('VIN')
        if info['has_obd']:
            indicators.append('OBD')
        
        if indicators:
            display_name += f" ({', '.join(indicators)})"

        filtered_models_data.append({
            'id': info['id'],
            'name': display_name
        })
    
    # Razvrstimo modele po imenu
    filtered_models_data.sort(key=lambda x: x['name'])

    return JsonResponse(filtered_models_data, safe=False)


def iskanje_vozil_view(request):
    # Pridobivanje vseh znamk in tipov vozil za začetno izbiro
    znamke = Znamka.objects.all().order_by('ime')
    tipi_vozil = TipVozila.objects.all().order_by('ime')
    
    # Pridobivanje parametrov iz GET zahtevka
    selected_znamka_id = request.GET.get('znamka')
    selected_tip_vozila_id = request.GET.get('tip_vozila')
    selected_model_id = request.GET.get('model') 
    leto_od_input = request.GET.get('leto_od')
    leto_do_input = request.GET.get('leto_do')
    vin_lokacija_opis_query = request.GET.get('vin_lokacija_opis_query', '').strip() 
    obd_lokacija_opis_query = request.GET.get('obd_lokacija_opis_query', '').strip() 

    # Začnemo s filtriranjem VoziloPodrobnosti, saj so na njih polja leto_od in leto_do ter lokacije
    vozila_podrobnosti_queryset = VoziloPodrobnosti.objects.all().select_related(
        'car_model__znamka', 
        'car_model__tip_vozila',
        'lokacija_vin_opis',
        'lokacija_obd_opis',
        'ilustracija_vin',
        'ilustracija_obd'
    ).order_by('car_model__znamka__ime', 'car_model__ime', 'leto_od')

    # Filtriranje po znamki (preko car_model)
    if selected_znamka_id:
        vozila_podrobnosti_queryset = vozila_podrobnosti_queryset.filter(car_model__znamka_id=selected_znamka_id)
    
    # Filtriranje po tipu vozila (preko car_model)
    if selected_tip_vozila_id:
        vozila_podrobnosti_queryset = vozila_podrobnosti_queryset.filter(car_model__tip_vozila_id=selected_tip_vozila_id)

    # Filtriranje po modelu (preko car_model)
    if selected_model_id:
        vozila_podrobnosti_queryset = vozila_podrobnosti_queryset.filter(car_model_id=selected_model_id)

    # Filtriranje po letih "od" in "do" iz VoziloPodrobnosti modela
    if leto_od_input or leto_do_input:
        try:
            leto_od_int = int(leto_od_input) if leto_od_input else None
            leto_do_int = int(leto_do_input) if leto_do_input else None

            conditions = Q()

            if leto_od_int:
                conditions &= (
                    Q(leto_do__gte=leto_od_int) | Q(leto_do__isnull=True)
                )

            if leto_do_int:
                conditions &= (
                    Q(leto_od__lte=leto_do_int) | Q(leto_od__isnull=True)
                )
            
            # Dodatna preverba za logiko, če je podano samo eno leto
            # Ta logika je lahko kompleksna in zahteva natančno testiranje z vsemi kombinacijami podatkov
            if leto_od_int and not leto_do_int:
                # Model se začne v iskanem letu_od ali prej IN se konča v iskanem letu_od ali kasneje (ali nima konca)
                conditions &= (Q(leto_od__lte=leto_od_int) & (Q(leto_do__gte=leto_od_int) | Q(leto_do__isnull=True))) | \
                              (Q(leto_od__gte=leto_od_int) & Q(leto_do__isnull=True)) # Model se začne po iskanem letu_od in nima konca (še aktualen)
            elif leto_do_int and not leto_od_int:
                # Model se začne pred iskanim letom_do (ali nima začetka) IN se konča v iskanem letu_do ali kasneje
                conditions &= (Q(leto_od__lte=leto_do_int) | Q(leto_od__isnull=True)) & \
                              (Q(leto_do__gte=leto_do_int) | Q(leto_do__isnull=True))
            
            vozila_podrobnosti_queryset = vozila_podrobnosti_queryset.filter(conditions)

        except ValueError:
            pass # Ignoriramo neveljaven vnos letnic

    # Filtriranje po ključnih besedah za VIN in OBD lokacijo
    if vin_lokacija_opis_query:
        vozila_podrobnosti_queryset = vozila_podrobnosti_queryset.filter(
            Q(lokacija_vin_opis__opis__icontains=vin_lokacija_opis_query)
        )
    
    if obd_lokacija_opis_query:
        vozila_podrobnosti_queryset = vozila_podrobnosti_queryset.filter(
            Q(lokacija_obd_opis__opis__icontains=obd_lokacija_opis_query)
        )

    # Priprava podatkov za JavaScript (popularne znamke, ostale znamke, znamke po tipu)
    popularne_znamke = list(Znamka.objects.filter(je_popularna=True).order_by('ime').values('id', 'ime'))
    ostale_znamke = list(Znamka.objects.filter(je_popularna=False).order_by('ime').values('id', 'ime'))
    all_znamke = list(Znamka.objects.all().order_by('ime').values('id', 'ime'))

    # Slovar znamk po tipu vozila za filtriranje v JS
    znamke_po_tipu = {}
    for tip in TipVozila.objects.all():
        # Dobimo vse znamke, ki imajo CarModel povezan s tem tipom vozila
        znamke_ids = CarModel.objects.filter(tip_vozila=tip).values_list('znamka__id', flat=True).distinct()
        znamke_po_tipu[str(tip.id)] = list(znamke_ids) # Ključ mora biti string za JSON

    context = {
        'znamke': znamke, 
        'tipi_vozil': tipi_vozil,
        'results': vozila_podrobnosti_queryset, 
        'selected_znamka_id': selected_znamka_id,
        'selected_tip_vozila_id': selected_tip_vozila_id,
        'selected_model_id': selected_model_id, 
        'leto_od': leto_od_input,
        'leto_do': leto_do_input,
        'vin_lokacija_opis_query': vin_lokacija_opis_query, 
        'obd_lokacija_opis_query': obd_lokacija_opis_query, 
        'popularne_znamke_data': popularne_znamke,
        'ostale_znamke_data': ostale_znamke,
        'all_znamke_data': all_znamke,
        'znamke_po_tipu': znamke_po_tipu,
    }
    return render(request, 'iskanje_vozil.html', context)