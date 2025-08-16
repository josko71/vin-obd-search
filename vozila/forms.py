# vozila/forms.py
from django import forms
from .models import TipVozila

class ChangeTipVozilaForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.HiddenInput)
    novi_tip_vozila = forms.ModelChoiceField(
        queryset=TipVozila.objects.all(),
        label="Novi tip vozila",
        empty_label="Izberite tip vozila",
    )