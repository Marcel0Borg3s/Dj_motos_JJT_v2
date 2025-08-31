from django.contrib import admin
from .models import Moto, ImagemMoto 

class ImagemMotoInline(admin.TabularInline):
    model = ImagemMoto
    extra = 1  # Mostra 1 campo de upload extra por padrão

class MotoAdmin(admin.ModelAdmin):
    list_display = ('model', 'brand', 'factor_year', 'model_year', 'value')
    search_fields = ('model', 'brand')
    inlines = [ImagemMotoInline] # 4. Adicione esta linha

admin.site.register(Moto, MotoAdmin)
