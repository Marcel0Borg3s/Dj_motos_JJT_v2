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
    
 