from django.contrib import admin
from django.urls import path, include # Odstranimo 'include', če ga ne uporabljamo drugje
from vozila import views as vozila_views # Uvozite views iz vaše aplikacije 'vozila'
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Glavni URL za prikaz strani za iskanje vozil
    # To je pot, ki jo brskalnik zahteva: http://127.0.0.1:8000/iskanje/
    path('', include('vozila.urls')),  # Vključite URL-je iz aplikacije 'vozila'
    path('ajax/get_models/', vozila_views.get_models_ajax, name='get_models_ajax'),  # Vključite URL-je iz aplikacije 'vozila'
]

# Serviranje medijskih datotek med razvojem
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)