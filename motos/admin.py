from django.contrib import admin
from .models import Motos, Brand

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class MotosAdmin(admin.ModelAdmin):
    list_display = ('model', 'brand', 'factor_year', 'model_year', 'value')
    search_fields = ('model', )

admin.site.register(Brand, BrandAdmin)
admin.site.register(Motos, MotosAdmin)
