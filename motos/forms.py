from django import forms
from motos.models import Motos

# class MotoForm(forms.Form):
#     model = forms.CharField(max_length=200)
#     # brand = forms.ModelChoiceField(Brand.objects.all())
#     factor_year = forms.IntegerField()
#     model_year = forms.IntegerField()
#     plate = forms.CharField(max_length=10)
#     value = forms.FloatField()
#     photo = forms.ImageField()

    # def save(self): 
    #     moto = Motos(
    #         model=self.cleaned_data['model'],
    #         brand=self.cleaned_data['brand'],
    #         factor_year=self.cleaned_data['factor_year'],
    #         model_year=self.cleaned_data['model_year'],
    #         plate=self.cleaned_data['plate'],
    #         value=self.cleaned_data['value'],
    #         photo=self.cleaned_data['photo'],
    #     )
        # moto.save()
        # return moto

class MotoModelForm(forms.ModelForm):
    class Meta:
        model = Motos
        fields = '__all__'       
    
    # Crianda validação/erros a partir de dados definidos
    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value <= 999:
            self.add_error('value', "O valor deve ser maior que 999.")
        return value
    
    def clean_factor_year(self):
        factor_year = self.cleaned_data.get('factor_year')
        if factor_year < 1980:
            self.add_error('factor_year', "O ano do fator deve ser maior ou igual a 1980.")
        return factor_year