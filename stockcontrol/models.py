"""
Modelos do sistema de Controle de Estoque e Custos (FASE 2).

Cada modelo é documentado com seus campos, finalidade e regras de negócio.
"""

from django.db import models
from django.core.validators import MinValueValidator
from motos.models import Motos


class MotoStock(models.Model):
    """
    Controle financeiro individual de cada moto.

    Registra todos os custos associados à aquisição, documentação,
    transporte, manutenção e outras despesas. Também armazena os dados
    de venda quando a moto é comercializada.

    Propriedades calculadas:
        - total_cost: soma de todos os custos
        - profit: lucro (sale_value - total_cost)
        - profit_margin: percentual de lucro sobre o custo total
    """

    class SaleStatus(models.TextChoices):
        """Status de comercialização da moto no estoque."""
        AVAILABLE = 'available', 'Disponível'
        SOLD = 'sold', 'Vendida'
        HIDDEN = 'hidden', 'Oculta do site'

    # Vínculo obrigatório com a moto (1 para 1)
    moto = models.OneToOneField(
        Motos,
        on_delete=models.CASCADE,
        related_name='stock',
        verbose_name='Moto',
        help_text='Moto vinculada a este controle de estoque.',
    )

    # ---- Custos estruturados ----
    acquisition_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Custo de aquisição',
        help_text='Valor pago na compra da moto (entrada).',
    )
    document_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Despesas de documento',
        help_text='Taxas de documentação, transferência, licenciamento.',
    )
    transport_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Transporte/frete',
        help_text='Custo de transporte, frete ou transferência.',
    )
    maintenance_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Manutenção/preparação',
        help_text='Gastos com revisão, preparação, reparos.',
    )
    fines_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Multas',
        help_text='Multas pendentes ou pagas.',
    )
    other_costs = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Outras despesas',
        help_text='Campo para despesas não previstas nas categorias acima.',
    )

    # ---- Dados de venda e exibição ----
    show_price = models.BooleanField(
        default=True,
        verbose_name='Exibir preço no site',
        help_text='Se desmarcado, mostra "Consulte-nos" no lugar do valor.',
    )
    sale_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Valor da venda',
        help_text='Preço final de venda. Preencha ao vender a moto.',
    )
    sale_status = models.CharField(
        max_length=20,
        choices=SaleStatus.choices,
        default=SaleStatus.AVAILABLE,
        verbose_name='Status',
        help_text='Situação atual da moto no estoque.',
    )
    sale_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data da venda',
        help_text='Data em que a moto foi vendida.',
    )
    buyer_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Nome do comprador',
    )
    buyer_document = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='CPF/CNPJ do comprador',
    )
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='Forma de pagamento',
        help_text='Ex: à vista, financiamento, Pix, cartão.',
    )

    # ---- Observações ----
    additional_notes = models.TextField(
        blank=True,
        default='',
        verbose_name='Observações',
        help_text='Anotações adicionais sobre custos ou venda.',
    )

    # ---- Controle de datas ----
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    # ---- Propriedades calculadas ----

    @property
    def total_cost(self) -> float:
        """Soma de todos os custos registrados para esta moto."""
        return (
            float(self.acquisition_cost)
            + float(self.document_fees)
            + float(self.transport_cost)
            + float(self.maintenance_cost)
            + float(self.fines_cost)
            + float(self.other_costs)
        )

    @property
    def profit(self):
        """
        Lucro obtido com a venda (sale_value - total_cost).
        Retorna None se a moto ainda não foi vendida.
        """
        if self.sale_value is None:
            return None
        return float(self.sale_value) - self.total_cost

    @property
    def profit_margin(self):
        """
        Margem de lucro percentual.
        Retorna None se a moto ainda não foi vendida ou custo total é zero.
        """
        if self.profit is None or self.total_cost == 0:
            return None
        return (self.profit / self.total_cost) * 100

    @property
    def is_sold(self) -> bool:
        """Indica se a moto foi vendida."""
        return self.sale_status == self.SaleStatus.SOLD

    @property
    def is_hidden(self) -> bool:
        """Indica se a moto está oculta do site."""
        return self.sale_status == self.SaleStatus.HIDDEN

    class Meta:
        verbose_name = 'Controle de Estoque'
        verbose_name_plural = 'Controles de Estoque'
        ordering = ['-created_at']

    def __str__(self):
        return f'Estoque: {self.moto.brand} {self.moto.model} (R$ {self.total_cost:.2f})'


class ExtraExpense(models.Model):
    """
    Despesa extra não prevista nas categorias padrão do MotoStock.

    Pode ser vinculada a uma moto específica (via FK) ou ser uma despesa
    geral do negócio (quando moto é None).

    Categorias disponíveis em Category.
    """

    class Category(models.TextChoices):
        """Categorias de despesas operacionais."""
        ADMIN = 'admin', 'Administrativo'
        MARKETING = 'marketing', 'Marketing / Publicidade'
        RENT = 'rent', 'Aluguel'
        SALARY = 'salary', 'Salários / Pró-labore'
        TAX = 'tax', 'Impostos / Taxas'
        TOOLS = 'tools', 'Ferramentas / Equipamentos'
        OTHER = 'other', 'Outros'

    # Vínculo opcional com uma moto
    moto = models.ForeignKey(
        Motos,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='extra_expenses',
        verbose_name='Moto (opcional)',
        help_text='Se esta despesa está vinculada a uma moto específica.',
    )

    description = models.CharField(
        max_length=300,
        verbose_name='Descrição',
        help_text='Descreva a despesa de forma clara e objetiva.',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Valor (R$)',
        help_text='Valor da despesa.',
    )
    date = models.DateField(
        verbose_name='Data',
        help_text='Data em que a despesa foi realizada.',
    )
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name='Categoria',
        help_text='Classificação da despesa.',
    )
    notes = models.TextField(
        blank=True,
        default='',
        verbose_name='Observações',
        help_text='Informações complementares.',
    )

    # ---- Controle de datas ----
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )

    class Meta:
        verbose_name = 'Despesa Extra'
        verbose_name_plural = 'Despesas Extras'
        ordering = ['-date', '-created_at']

    def __str__(self):
        vinculo = f' [{self.moto.brand} {self.moto.model}]' if self.moto else ''
        return f'{self.description} - R$ {self.amount:.2f}{vinculo}'
