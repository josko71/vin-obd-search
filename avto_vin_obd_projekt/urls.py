from django.contrib import admin
from django.urls import path, include
from vozila import views as vozila_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('vozila.urls')),
    path('ajax/get_models/', vozila_views.get_models_ajax, name='get_models_ajax'),
]

# Serviranje statičnih in medijskih datotek med razvojem
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar (samo če je v settings/dev.py)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
        