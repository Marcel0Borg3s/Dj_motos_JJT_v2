from django import forms
from motos.models import Motos, Brand

class MotoModelForm(forms.ModelForm):
    brand = forms.CharField(
        label='Marca',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Yamaha, Honda, BMW...'}),
        required=True,
    )

    class Meta:
        model = Motos
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se estiver editando, usa o nome da marca (não o PK) no campo brand
        if self.instance and self.instance.pk and self.instance.brand:
            nome = self.instance.brand.name
            self.fields['brand'].initial = nome
            self.initial['brand'] = nome

    def clean_brand(self):
        name = self.cleaned_data.get('brand', '').strip()
        if not name:
            raise forms.ValidationError("Informe a marca da moto.")
        # Busca a Brand ignorando capitalização; se não existir, cria
        brand, _ = Brand.objects.get_or_create(name__iexact=name, defaults={'name': name})
        return brand

    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value in [None, ""]:
            return None
        if value <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero!")
        return value

    def clean_factor_year(self):
        factor_year = self.cleaned_data.get('factor_year')
        if factor_year and factor_year < 1980:
            self.add_error('factor_year', "O ano do fator deve ser maior ou igual a 1980.")
        return factor_year