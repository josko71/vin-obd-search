from django.contrib import admin
from django.urls import path, include
from vozila import views as vozila_views
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('vozila.urls')),
    path('ajax/get_models/', vozila_views.get_models_ajax, name='get_models_ajax'),
]

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns