from django.contrib import admin
from .models import Motos, Brand, ImagemMoto

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ImagemMotoInline(admin.TabularInline):
    model = ImagemMoto
    extra = 1 

class MotosAdmin(admin.ModelAdmin):
    list_display = ('model', 'brand', 'factor_year', 'model_year', 'value')
    inlines = [ImagemMotoInline]
    search_fields = ('model', )

admin.site.register(Brand, BrandAdmin)
admin.site.register(Motos, MotosAdmin)
