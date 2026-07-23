"""
Formulários do módulo de Controle de Estoque.

Cada form é responsável por um aspecto específico:
    - StockCostForm: edição dos custos de uma moto
    - SaleForm: registro de venda
    - ExtraExpenseForm: despesas extras
"""

from django import forms
from stockcontrol.models import MotoStock, ExtraExpense


class StockCostForm(forms.ModelForm):
    """
    Formulário para editar os custos de aquisição e manutenção de uma moto.

    Todos os campos de custo são opcionais (default=0) para permitir
    que o usuário preencha apenas os que deseja.
    """

    class Meta:
        model = MotoStock
        fields = [
            'acquisition_cost',
            'document_fees',
            'transport_cost',
            'maintenance_cost',
            'fines_cost',
            'other_costs',
            'additional_notes',
        ]
        widgets = {
            'acquisition_cost': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': '0,00', 'step': '0.01',
            }),
            'document_fees': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': '0,00', 'step': '0.01',
            }),
            'transport_cost': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': '0,00', 'step': '0.01',
            }),
            'maintenance_cost': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': '0,00', 'step': '0.01',
            }),
            'fines_cost': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': '0,00', 'step': '0.01',
            }),
            'other_costs': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': '0,00', 'step': '0.01',
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-textarea', 'placeholder': 'Observações sobre custos...',
                'rows': 3,
            }),
        }
        labels = {
            'acquisition_cost': 'Custo de aquisição (R$)',
            'document_fees': 'Despesas de documento (R$)',
            'transport_cost': 'Transporte/frete (R$)',
            'maintenance_cost': 'Manutenção/preparação (R$)',
            'fines_cost': 'Multas (R$)',
            'other_costs': 'Outras despesas (R$)',
            'additional_notes': 'Observações',
        }


class SaleForm(forms.ModelForm):
    """
    Formulário para registrar a venda de uma moto.

    Ao salvar, altera o sale_status para 'sold' e registra a data.
    """

    class Meta:
        model = MotoStock
        fields = [
            'sale_value',
            'buyer_name',
            'buyer_document',
            'payment_method',
            'sale_date',
        ]
        widgets = {
            'sale_value': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Valor da venda',
                'step': '0.01',
            }),
            'buyer_name': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Nome completo do comprador',
            }),
            'buyer_document': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'CPF ou CNPJ',
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
            }),
            'sale_date': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date',
            }),
        }
        labels = {
            'sale_value': 'Valor da venda (R$)',
            'buyer_name': 'Nome do comprador',
            'buyer_document': 'CPF/CNPJ',
            'payment_method': 'Forma de pagamento',
            'sale_date': 'Data da venda',
        }

    def __init__(self, *args, **kwargs):
        """Preenche a data atual como padrão e define choices de pagamento."""
        super().__init__(*args, **kwargs)
        from datetime import date
        if not self.instance.sale_date:
            self.fields['sale_date'].initial = date.today().isoformat()

    def clean_sale_value(self):
        """Valida que o valor da venda é positivo."""
        value = self.cleaned_data.get('sale_value')
        if value is not None and value <= 0:
            raise forms.ValidationError('O valor da venda deve ser maior que zero.')
        return value


# Choices para o campo payment_method (não está no model, mas usamos no form)
SaleForm.Meta.model._meta.get_field('payment_method').choices = [
    ('', 'Selecione...'),
    ('pix', 'Pix'),
    ('dinheiro', 'Dinheiro'),
    ('cartao_credito', 'Cartão de crédito'),
    ('cartao_debito', 'Cartão de débito'),
    ('financiamento', 'Financiamento'),
    ('consorcio', 'Consórcio'),
    ('transferencia', 'Transferência bancária'),
    ('outro', 'Outro'),
]


class ExtraExpenseForm(forms.ModelForm):
    """
    Formulário para lançar despesas extras.

    Pode ser vinculada a uma moto específica ou ser uma despesa geral.
    """

    class Meta:
        model = ExtraExpense
        fields = ['moto', 'description', 'amount', 'date', 'category', 'notes']
        widgets = {
            'moto': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Descrição da despesa',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': '0,00', 'step': '0.01',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date',
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea', 'placeholder': 'Observações (opcional)',
                'rows': 3,
            }),
        }
        labels = {
            'moto': 'Moto (opcional)',
            'description': 'Descrição',
            'amount': 'Valor (R$)',
            'date': 'Data',
            'category': 'Categoria',
            'notes': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        """Preenche a data atual e filtra motos disponíveis."""
        super().__init__(*args, **kwargs)
        from datetime import date
        if not self.instance.pk:
            self.fields['date'].initial = date.today().isoformat()
        # Limita o select de motos às que têm estoque ou estão disponíveis
        self.fields['moto'].queryset = self.fields['moto'].queryset.order_by(
            'brand__name', 'model'
        )
        self.fields['moto'].required = False
        self.fields['moto'].label = 'Moto (opcional - deixe em branco para despesa geral)'
