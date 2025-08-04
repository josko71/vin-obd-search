from django.contrib import admin
from django.urls import path, include
from vozila import views as vozila_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('iskanje/', include('vozila.urls')), # Spremenite to vrstico
    path('ajax/get_models/', vozila_views.get_models_ajax, name='get_models_ajax'),
]

# Serviranje medijskih datotek med razvojem
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)