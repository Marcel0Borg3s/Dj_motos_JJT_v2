from django.contrib import admin
from stockcontrol.models import MotoStock, ExtraExpense


@admin.register(MotoStock)
class MotoStockAdmin(admin.ModelAdmin):
    list_display = ['moto', 'total_cost', 'sale_status', 'sale_value', 'profit']
    list_filter = ['sale_status']


@admin.register(ExtraExpense)
class ExtraExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'moto', 'amount', 'date', 'category']
    list_filter = ['category', 'date']
