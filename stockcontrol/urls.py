"""
URLs do módulo de Controle de Estoque.

Todas as rotas são prefixadas com /stock/ e protegidas pelo
decorator financeiro_required (exceto quando indicado).
"""

from django.urls import path
from stockcontrol import views

app_name = 'stockcontrol'

urlpatterns = [
    # Dashboard principal
    path('',
         views.StockDashboardView.as_view(),
         name='dashboard'),

    # Lista de estoque (planilha)
    path('motos/',
         views.StockListView.as_view(),
         name='stock_list'),

    # Custos detalhados de uma moto
    path('motos/<int:pk>/',
         views.StockDetailView.as_view(),
         name='stock_detail'),

    # Editar custos de uma moto
    path('motos/<int:pk>/custos/',
         views.StockCostUpdateView.as_view(),
         name='stock_cost_edit'),

    # Registrar venda de uma moto
    path('motos/<int:pk>/vender/',
         views.SaleCreateView.as_view(),
         name='stock_sale'),

    # Despesas extras
    path('despesas/',
         views.ExpenseListView.as_view(),
         name='expense_list'),
    path('despesas/nova/',
         views.ExpenseCreateView.as_view(),
         name='expense_new'),
    path('despesas/<int:pk>/editar/',
         views.ExpenseUpdateView.as_view(),
         name='expense_edit'),
    path('despesas/<int:pk>/excluir/',
         views.ExpenseDeleteView.as_view(),
         name='expense_delete'),

    # Toggle visibilidade
    path('motos/<int:pk>/ocultar/',
         views.StockToggleHiddenView.as_view(),
         name='stock_toggle_hidden'),
    path('motos/<int:pk>/exibir/',
         views.StockToggleVisibleView.as_view(),
         name='stock_toggle_visible'),
]
