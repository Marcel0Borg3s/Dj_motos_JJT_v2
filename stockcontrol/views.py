"""
Views do módulo de Controle de Estoque (FASE 2).

Organizadas por funcionalidade:
    1. Dashboard - visão geral com cards e gráfico
    2. Lista de Estoque - planilha de motos com custos
    3. Detalhe de Custos - custos individuais de cada moto
    4. Vendas - registrar venda
    5. Despesas - CRUD de despesas extras
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, DetailView,
    UpdateView, CreateView, DeleteView, View,
)
from django.utils.decorators import method_decorator
from django.db.models import Sum, Count, Q
from django.contrib import messages
from datetime import datetime, date

from motos.models import Motos
from stockcontrol.models import MotoStock, ExtraExpense
from stockcontrol.forms import StockCostForm, SaleForm, ExtraExpenseForm
from stockcontrol.decorators import financeiro_required


# =============================================================================
# 1. DASHBOARD
# =============================================================================

@method_decorator(financeiro_required, name='dispatch')
class StockDashboardView(TemplateView):
    """
    Dashboard principal do controle de estoque.

    Exibe cards de resumo e a listagem rápida das motos com filtros
    por mês/ano e status.
    """
    template_name = 'stockcontrol/dashboard.html'

    def get_context_data(self, **kwargs):
        """Monta o contexto com dados agregados do estoque."""
        ctx = super().get_context_data(**kwargs)

        # Filtros opcionais
        month = self.request.GET.get('mes', '')
        year = self.request.GET.get('ano', '')

        # Base: todos os registros de estoque
        stocks = MotoStock.objects.select_related('moto__brand')

        # Filtra por vendas no período, se informado
        stocks_sold = stocks.filter(sale_status='sold')
        if month and month.isdigit():
            stocks_sold = stocks_sold.filter(sale_date__month=int(month))
        if year and year.isdigit():
            stocks_sold = stocks_sold.filter(sale_date__year=int(year))

        # ---- Cards de resumo ----
        total_motos = stocks.count()
        motos_disponiveis = stocks.filter(sale_status='available').count()
        motos_vendidas = stocks_sold.count()

        # Valor total em estoque (custo)
        valor_estoque = sum(s.total_cost for s in stocks.filter(sale_status='available'))

        # Lucro total das vendas no período
        lucro_total = sum(s.profit or 0 for s in stocks_sold)

        # Total de despesas extras
        despesas = ExtraExpense.objects.all()
        if month and month.isdigit():
            despesas = despesas.filter(date__month=int(month))
        if year and year.isdigit():
            despesas = despesas.filter(date__year=int(year))
        total_despesas = sum(float(d.amount) for d in despesas)

        # Últimas 5 vendas
        ultimas_vendas = stocks.filter(
            sale_status='sold'
        ).select_related('moto__brand').order_by('-sale_date')[:5]

        ctx.update({
            'total_motos': total_motos,
            'motos_disponiveis': motos_disponiveis,
            'motos_vendidas': motos_vendidas,
            'valor_estoque': valor_estoque,
            'lucro_total': lucro_total,
            'total_despesas': total_despesas,
            'ultimas_vendas': ultimas_vendas,
            'stocks': stocks.select_related('moto__brand').order_by('-created_at')[:20],
            'mes_atual': month or '',
            'ano_atual': year or '',
            'meses': [
                (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
                (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
                (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
                (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
            ],
        })
        return ctx


# =============================================================================
# 2. LISTA DE ESTOQUE (PLANILHA)
# =============================================================================

@method_decorator(financeiro_required, name='dispatch')
class StockListView(ListView):
    """
    Lista todas as motos com seus custos em formato de planilha.

    Exibe colunas: Moto, Custo Total, Valor Venda, Margem, Status.
    Permite ações por linha.
    """
    model = MotoStock
    template_name = 'stockcontrol/stock_list.html'
    context_object_name = 'stocks'

    def get_queryset(self):
        """Retorna os registros ordenados por status e data."""
        qs = super().get_queryset().select_related('moto__brand')
        # Filtro por status
        status = self.request.GET.get('status', '')
        if status in ('available', 'sold', 'hidden'):
            qs = qs.filter(sale_status=status)
        return qs.order_by('sale_status', '-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_atual'] = self.request.GET.get('status', '')
        return ctx


# =============================================================================
# 3. DETALHE DE CUSTOS
# =============================================================================

@method_decorator(financeiro_required, name='dispatch')
class StockDetailView(DetailView):
    """
    Exibe todos os custos detalhados de uma moto específica.

    Inclui o total calculado, o lucro (se vendida) e lista as
    despesas extras vinculadas.
    """
    model = MotoStock
    template_name = 'stockcontrol/stock_detail.html'
    context_object_name = 'stock'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Despesas extras vinculadas a esta moto
        ctx['extra_expenses'] = ExtraExpense.objects.filter(
            moto=self.object.moto
        ).order_by('-date')
        # Custo total incluindo despesas extras
        extra_total = sum(
            float(e.amount) for e in ctx['extra_expenses']
        )
        ctx['custo_total_geral'] = self.object.total_cost + extra_total
        return ctx


# =============================================================================
# 4. EDITAR CUSTOS
# =============================================================================

@method_decorator(financeiro_required, name='dispatch')
class StockCostUpdateView(UpdateView):
    """
    View para editar os custos de aquisição e manutenção de uma moto.

    Se o registro MotoStock não existir para a moto, ele é criado
    automaticamente (via get_object).
    """
    model = MotoStock
    form_class = StockCostForm
    template_name = 'stockcontrol/expense_form.html'

    def get_object(self, queryset=None):
        """
        Retorna o MotoStock para o pk informado na URL.
        O pk é o ID do registro MotoStock (não da Motos).
        """
        return get_object_or_404(MotoStock, pk=self.kwargs.get('pk'))

    def get_success_url(self):
        """Redireciona para o detalhe da moto no estoque."""
        messages.success(self.request, 'Custos atualizados com sucesso!')
        return reverse_lazy('stockcontrol:stock_detail', kwargs={'pk': self.object.pk})


# =============================================================================
# 5. REGISTRAR VENDA
# =============================================================================

@method_decorator(financeiro_required, name='dispatch')
class SaleCreateView(UpdateView):
    """
    View para registrar a venda de uma moto.

    Ao salvar com sucesso, altera o status para 'sold' e registra
    a data da venda automaticamente se não informada.
    """
    model = MotoStock
    form_class = SaleForm
    template_name = 'stockcontrol/sale_form.html'

    def get_object(self, queryset=None):
        """Retorna o MotoStock pelo pk informado na URL."""
        return get_object_or_404(MotoStock, pk=self.kwargs.get('pk'))

    def form_valid(self, form):
        """
        Ao salvar, altera o status para 'sold' e registra a data.
        """
        self.object = form.save(commit=False)
        self.object.sale_status = MotoStock.SaleStatus.SOLD
        if not self.object.sale_date:
            self.object.sale_date = date.today()
        self.object.save()
        messages.success(
            self.request,
            f'Venda registrada! Lucro: R$ {self.object.profit:.2f}'
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('stockcontrol:stock_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['custo_total'] = self.object.total_cost
        return ctx


# =============================================================================
# 6. DESPESAS EXTRAS — CRUD
# =============================================================================

@method_decorator(financeiro_required, name='dispatch')
class ExpenseListView(ListView):
    """
    Lista todas as despesas extras cadastradas.

    Ordenadas por data (mais recentes primeiro).
    Filtro opcional por categoria.
    """
    model = ExtraExpense
    template_name = 'stockcontrol/extra_expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset().select_related('moto__brand')
        cat = self.request.GET.get('categoria', '')
        if cat:
            qs = qs.filter(category=cat)
        return qs.order_by('-date', '-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categoria_atual'] = self.request.GET.get('categoria', '')
        ctx['total'] = sum(
            float(e.amount) for e in self.get_queryset()
        )
        return ctx


@method_decorator(financeiro_required, name='dispatch')
class ExpenseCreateView(CreateView):
    """
    Cria uma nova despesa extra.
    Pode ser vinculada a uma moto ou ser geral.
    """
    model = ExtraExpense
    form_class = ExtraExpenseForm
    template_name = 'stockcontrol/extra_expense_form.html'
    success_url = reverse_lazy('stockcontrol:expense_list')

    def form_valid(self, form):
        messages.success(self.request, 'Despesa cadastrada com sucesso!')
        return super().form_valid(form)


@method_decorator(financeiro_required, name='dispatch')
class ExpenseUpdateView(UpdateView):
    """
    Edita uma despesa extra existente.
    """
    model = ExtraExpense
    form_class = ExtraExpenseForm
    template_name = 'stockcontrol/extra_expense_form.html'
    success_url = reverse_lazy('stockcontrol:expense_list')

    def form_valid(self, form):
        messages.success(self.request, 'Despesa atualizada com sucesso!')
        return super().form_valid(form)


@method_decorator(financeiro_required, name='dispatch')
class ExpenseDeleteView(DeleteView):
    """
    Exclui uma despesa extra com confirmação.
    """
    model = ExtraExpense
    template_name = 'stockcontrol/extra_expense_confirm_delete.html'
    success_url = reverse_lazy('stockcontrol:expense_list')

    def form_valid(self, form):
        messages.success(self.request, 'Despesa excluída com sucesso!')
        return super().form_valid(form)


# =============================================================================
# 7. STATUS TOGGLE — Ocultar / Exibir / Reexibir
# =============================================================================

@method_decorator(financeiro_required, name='dispatch')
class StockToggleHiddenView(View):
    """
    Alterna o status da moto para 'hidden' (oculta do site público).
    """
    def get(self, request, pk):
        stock = get_object_or_404(MotoStock, pk=pk)
        stock.sale_status = MotoStock.SaleStatus.HIDDEN
        stock.save()
        messages.success(request, 'Moto ocultada do site público.')
        return redirect('stockcontrol:stock_detail', pk=pk)


@method_decorator(financeiro_required, name='dispatch')
class StockToggleVisibleView(View):
    """
    Alterna o status da moto de volta para 'available' (visível no site).
    """
    def get(self, request, pk):
        stock = get_object_or_404(MotoStock, pk=pk)
        stock.sale_status = MotoStock.SaleStatus.AVAILABLE
        stock.save()
        messages.success(request, 'Moto agora está visível no site.')
        return redirect('stockcontrol:stock_detail', pk=pk)


@method_decorator(financeiro_required, name='dispatch')
class StockTogglePriceView(View):
    """
    Alterna a flag show_price entre True e False.
    Quando False, o preço não aparece no site público (mostra "Consulte-nos").
    """
    def get(self, request, pk):
        stock = get_object_or_404(MotoStock, pk=pk)
        stock.show_price = not stock.show_price
        stock.save()
        status = 'agora visível' if stock.show_price else 'ocultado'
        messages.success(request, f'Preço {status} no site público.')
        return redirect('stockcontrol:stock_detail', pk=pk)
