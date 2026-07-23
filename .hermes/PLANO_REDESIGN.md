# Plano de Redesign — JJT Motorcycles

## Sumário Executivo

Migrar o visual atual (Bootstrap + CSS genérico) para um layout inspirado no
**Ferrari Design System** — clássico, elegante, tipografia refinada e botões
com cantos vivos (2px radius). O fundo com o logo da JJT em baixa opacidade
será mantido. Toda a funcionalidade existente será preservada.

---

## FASE 1 — Layout Ferrari (REDESIGN VISUAL)

### 1. Design Tokens (CSS custom properties)

Substituir o `custom.css` atual por um sistema de variáveis baseado no
Ferrari Dark Theme:

```css
:root {
  --ferrari-red:       #DA291C;
  --dark-red:          #B01E0A;
  --deep-red:          #9D2211;
  --absolute-black:    #000000;
  --pure-white:        #FFFFFF;
  --near-black:        #181818;
  --dark-surface:      #303030;
  --dark-surface-lt:   #3A3A3A;
  --light-gray:        #D2D2D2;
  --dark-gray:         #666666;
  --mid-gray:          #8F8F8F;
  --silver-gray:       #969696;
  --border-dark:       #444444;

  /* Semânticos */
  --page-bg:           var(--near-black);
  --card-bg:           var(--dark-surface);
  --text-primary:      var(--pure-white);
  --text-secondary:    var(--light-gray);
  --text-muted:        var(--mid-gray);
  --divider:           var(--border-dark);

  /* Tipografia */
  --font-heading:      'DM Sans', Arial, Helvetica, sans-serif;
  --font-body:         'Barlow Condensed', Arial, Helvetica, sans-serif;

  /* Border radius Ferrari: 2px (sharp, precision) */
  --radius:            2px;
}
```

### 2. Navbar Reformulada

**Atual:** Header Bootstrap com flex simples, links soltos.
**Novo:** Sticky nav preta com:

- **Esquerda:** Logo JJT + nome "JJT Motorcycles"
- **Centro:** Links de navegação (Motos, WhatsApp)
- **Direita:** Botão CTA vermelho (Login / "Nova Moto" / "Sair")
- Botão Whatsapp com fundo verde e hover escuro

A navbar segue o padrão Ferrari: preta sólida, links em branco com
hover sutil, CTA vermelho.

### 3. Grid de Motos (Lista)

**Atual:** Cards com bordas arredondadas (8px), cor azul ciano como
destaque, sombras suaves.
**Novo:** Cards estilo Ferrari editorial — retos (2px radius, sem borda
arredondada), fundo `--dark-surface` com borda `1px solid #444`.

Cada card:
- Imagem no topo (200px height, cover)
- Abaixo: caption (LABEL UPPERCASE — Barlow Condensed 12px) tipo
  "Moto • 2024" ou "Novidade"
- Título: DM Sans 18px bold
- Info: Ano, modelo, preço
- Hover: leve translateY(-2px)

Search bar: campo escuro com borda que foca em vermelho Ferrari.

### 4. Detail da Moto

**Atual:** Carrossel + informações em grid simples.
**Novo:**
- Carrossel mantido (estilo Ferrari: cantos retos, setas sutis)
- Grid de specs em 2 colunas com labels uppercase
- Preço em destaque com fonte heading 24px bold
- Botões de ação (Editar/Deletar/Voltar) visíveis apenas para admin
- Layout limpo, tipografia precisa

### 5. Formulários (New/Edit)

**Atual:** `form.as_table` dentro de um container arredondado.
**Novo:**
- Grid de 2 colunas (Ferrari form style)
- Labels uppercase 12px Barlow Condensed, cor muted
- Inputs: fundo transparente, borda #444, focus em vermelho
- Botões no final: "Cadastrar" (verde) e "Cancelar"
- Upload de fotos com preview (melhoria)

### 6. Footer

**Atual:** Footer simples com direitos reservados.
**Novo:** Footer escuro (absolute-black) com:
- Logo JJT pequena + "JJT Motorcycles"
- CNPJ, endereço
- Créditos: "Desenvolvido por Marcelo Borges"
- Links GitHub, LinkedIn

### 7. Páginas de Auth (Login/Register)

**Atual:** Forms simples do Django.
**Novo:** Card centralizado com inputs Ferrari, botão CTA vermelho,
texto "Não tem conta? Registre-se" no mesmo estilo.

---

## FASE 2 — Controle de Estoque & Lucratividade (Backend)

### 2.1 — Novos Models

#### ProductStock (substitui/alimenta MotoInventory)

```python
class ProductStock(models.Model):
    moto = models.OneToOneField(Motos, on_delete=models.CASCADE)
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2)  # Custo de aquisição
    entry_value = models.DecimalField(max_digits=12, decimal_places=2)       # Valor de entrada
    document_fees = models.DecimalField(max_digits=10, decimal_places=2)     # Taxas documentação
    transport_cost = models.DecimalField(max_digits=10, decimal_places=2)    # Frete/transporte
    refurbish_cost = models.DecimalField(max_digits=10, decimal_places=2)    # Preparação/reforma
    other_costs = models.DecimalField(max_digits=10, decimal_places=2)       # Outras despesas
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)       # Auto-calculado
    status = models.CharField(choices=STATUS_CHOICES)                        # Em estoque, Vendido, Reservado
    entry_date = models.DateField(auto_now_add=True)
```

#### Sale

```python
class Sale(models.Model):
    moto = models.ForeignKey(Motos, on_delete=models.PROTECT)
    sale_value = models.DecimalField(max_digits=12, decimal_places=2)
    profit = models.DecimalField(max_digits=12, decimal_places=2)           # sale_value - total_cost
    sale_date = models.DateTimeField(auto_now_add=True)
    buyer_name = models.CharField(max_length=200)
    buyer_document = models.CharField(max_length=20, blank=True)
    payment_method = models.CharField(choices=PAYMENT_CHOICES)
    notes = models.TextField(blank=True)
```

#### Expense

```python
class Expense(models.Model):
    description = models.CharField(max_length=300)
    category = models.CharField(choices=EXPENSE_CATEGORIES)  # Aluguel, Marketing, Salários, etc.
    value = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    recurring = models.BooleanField(default=False)
```

### 2.2 — Dashboard (Staff/Admin only)

Página protegida por login com:

1. **Cards de resumo:**
   - Total de motos em estoque
   - Valor total em estoque (custo vs venda)
   - Lucro potencial total
   - Últimas vendas (5)

2. **Tabela de Estoque com custos:**
   - Grid com colunas: Moto, Custo Total, Valor Venda, Margem, Status
   - Ordenável por coluna
   - Ações: Editar custos, Marcar como vendido

3. **Gráfico de lucratividade** (opcional, Chart.js simples):
   - Lucro por mês
   - Despesas vs receitas

4. **Registro de Venda:**
   - Modal/form para lançar venda (selecionar moto, valor, comprador)
   - Auto-cálculo do lucro

### 2.3 — Novas Views (protegidas por login)

| URL | View | Descrição |
|-----|------|-----------|
| `/stock/` | StockDashboardView | Dashboard geral |
| `/stock/<pk>/edit/` | StockUpdateView | Editar custos de um item |
| `/stock/sale/new/` | SaleCreateView | Registrar venda |
| `/stock/sales/` | SaleListView | Histórico de vendas |
| `/stock/expenses/` | ExpenseListView | Despesas da empresa |
| `/stock/expenses/new/` | ExpenseCreateView | Nova despesa |

---

## Cronograma Sugerido

```
                    FASE 1 (Redesign Visual)
┌─────────────────────────────────────────────────┐
│ 1.1  Design Tokens + CSS Base          │  ✅    │
│ 1.2  Navbar                            │        │
│ 1.3  Grid de Motos + Search            │        │
│ 1.4  Detail + Carrossel                │        │
│ 1.5  Formulários (New/Edit)            │        │
│ 1.6  Auth (Login/Register)             │        │
│ 1.7  Delete Confirmation               │        │
│ 1.8  Footer                            │        │
│ 1.9  Testes visuais + ajustes          │        │
└─────────────────────────────────────────────────┘

                    FASE 2 (Estoque + Lucratividade)
┌─────────────────────────────────────────────────┐
│ 2.1  Models: ProductStock, Sale, Expense│        │
│ 2.2  Migrations                        │        │
│ 2.3  Dashboard (stock/)                │        │
│ 2.4  Editar Custos                     │        │
│ 2.5  Registrar Vendas                  │        │
│ 2.6  Histórico de Vendas               │        │
│ 2.7  Despesas                          │        │
│ 2.8  Sinais (automação total_cost)     │        │
│ 2.9  Testes + ajustes                  │        │
└─────────────────────────────────────────────────┘
```

---

## Estrutura de Arquivos (Fase 1)

```
app/
  static/
    css/
      ferrari.css          ← NOVO (design system completo)
      custom.css           ← removido (substituído por ferrari.css)
  templates/
    base.html              ← REFEITO (layout Ferrari)
    base_old.html          ← mantido como backup

motos/
  templates/
    motos.html             ← REFEITO (grid Ferrari)
    moto_detail.html       ← REFEITO (detalhe elegante)
    new_moto.html          ← REFEITO (form Ferrari)
    moto_update.html       ← REFEITO (form Ferrari)
    moto_delete.html       ← REFEITO (confirmação elegante)

accounts/
  templates/
    login.html             ← REFEITO (layout Ferrari)
    register.html          ← REFEITO (layout Ferrari)
```

---

## Decisões de Design

**Por que remover Bootstrap?**
O Bootstrap traz estilos genéricos que conflitam com a estética Ferrari
(cantos arredondados, sombras, azul padrão). A substituição por CSS puro
com variáveis dá controle total sobre cada pixel e reduz o payload.

**Paleta de Cores Principal:**
- Preto absoluto (#000) para navbar e hero
- Vermelho Ferrari (#DA291C) para CTAs e destaques
- Branco puro (#FFF) para texto primário
- Cinzas precisos para hierarquia de informação
- **Verde** (#03904A) para ações de confirmação (salvar, cadastrar)
- **Vermelho** (#F13A2C) para ações destrutivas (deletar)

**Tipografia:**
- DM Sans (sans-serif moderna) para headings e UI
- Barlow Condensed (compacta) para labels e metadados
- Monospace para valores hex, códigos
