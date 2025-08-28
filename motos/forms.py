from django import forms
from motos.models import Motos

class MotoModelForm(forms.ModelForm):
    class Meta:
        model = Motos
        fields = '__all__'       
    
    # Crianda validação/erros a partir de dados definidos
    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value in [None, ""]:
            return None
        if value <= 0:
            raise forms.ValidationError ("Ovalor deve ser maior que zero!")
        return value
    
    def clean_factor_year(self):
        factor_year = self.cleaned_data.get('factor_year')
        if factor_year < 1980:
            self.add_error('factor_year', "O ano do fator deve ser maior ou igual a 1980.")
        return factor_year