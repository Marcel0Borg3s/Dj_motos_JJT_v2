from django import forms
from .models import Motos, Brand


class MotoForm(forms.Form):
    model = forms.CharField(max_length=200)
    brand = forms.ModelsChoice(Brand, on_delete=models.PROTECT, related_name='motos_brand')
    factor_year = forms.models.IntegerField(blank=True, null=True)
    model_year = forms.odels.IntegerField(blank=True, null=True)
    plate = forms.CharField(max_length=10, blank=True, null=True)
    value = forms.FloatField(blank=True, null=True)
    photo = forms.ImageField(upload_to='motos/', blank=True, null=True)
