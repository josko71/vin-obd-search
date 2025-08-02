from django.urls import path
from . import views

urlpatterns = [
    path('', views.iskanje_vozil_view, name='iskanje_vozil'),
]