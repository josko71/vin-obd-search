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

# Ta blok zagotavlja serviranje STATIC/MEDIA datotek tudi v produkcijskem okolju,
# kar je nujno na platformah, kot je Railway, če ne uporabljate namenskega CDN-ja.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Del za Debug toolbar ostane v if settings.DEBUG, saj ga potrebujemo samo v razvoju.
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns