# PRD — Controle de Estoque e Lucratividade (FASE 2)

## Objetivo
Sistema integrado ao projeto JJT Motorcycles para controle financeiro de estoque,
custos por moto, registro de vendas, despesas operacionais e dashboard de
lucratividade. Acesso exclusivo para usuários do grupo **financeiro**.

## Arquitetura Final

```
stockcontrol/                  # App separado do motos/
├── PRD.md                     # Este documento
├── __init__.py
├── admin.py                   # Registro admin dos models
├── apps.py                    # AppConfig + ready() para sinais
├── decorators.py              # financeiro_required decorator
├── forms.py                   # StockCostForm, SaleForm, ExtraExpenseForm
├── models.py                  # MotoStock, ExtraExpense (documentados)
├── signals.py                 # Auto-cria MotoStock ao cadastrar Motos
├── urls.py                    # 12 rotas /stock/*
├── views.py                   # 11 views (dashboard, CRUD, toggles)
├── migrations/
│   ├── 0001_initial.py        # Tabelas MotoStock e ExtraExpense
│   └── 0002_criar_grupos.py   # Grupos financeiro e gerente
└── templates/stockcontrol/
    ├── base_stock.html        # Base com sidebar + navbar + toggle tema
    ├── dashboard.html         # Dashboard com cards e filtros
    ├── stock_list.html        # Planilha de estoque
    ├── stock_detail.html      # Custos detalhados + toggle ocultar
    ├── expense_form.html      # Formulário de edição de custos
    ├── sale_form.html         # Formulário de registro de venda
    ├── extra_expense_list.html  # Lista de despesas extras
    ├── extra_expense_form.html  # Nova/editar despesa extra
    └── extra_expense_confirm_delete.html  # Confirmar exclusão
```

## Modelos de Dados

### MotoStock (1:1 com Motos)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| moto | OneToOneField(Motos) | Vínculo com a moto |
| acquisition_cost | Decimal(12,2) | Valor de entrada (compra) |
| document_fees | Decimal(10,2) | Despesas de documento |
| transport_cost | Decimal(10,2) | Transferência/transporte |
| maintenance_cost | Decimal(10,2) | Manutenção/preparação |
| fines_cost | Decimal(10,2) | Multas |
| other_costs | Decimal(10,2) | Outras despesas não previstas |
| sale_value | Decimal(12,2,null) | Valor da venda (preenche ao vender) |
| sale_status | CharField(20) | available, sold, hidden |
| sale_date | Date(null) | Data da venda |
| buyer_name | CharField(200) | Nome do comprador |
| buyer_document | CharField(20) | CPF/CNPJ |
| payment_method | CharField(50) | Forma de pagamento |
| additional_notes | TextField | Observações sobre custos/venda |
| created_at | DateTime(auto) | Auto |
| updated_at | DateTime(auto) | Auto |

**Propriedades calculadas:**
- `total_cost` — soma de todos os custos (acquisition_cost + document_fees + ...)
- `profit` — sale_value - total_cost (None se não vendida)
- `profit_margin` — percentual de lucro sobre o custo
- `is_sold` — True se sale_status == 'sold'
- `is_hidden` — True se sale_status == 'hidden'

### ExtraExpense
| Campo | Tipo | Descrição |
|-------|------|-----------|
| moto | FK(Motos, null) | Vinculado a uma moto específica ou geral |
| description | CharField(300) | Descrição da despesa |
| amount | Decimal(12,2) | Valor |
| date | Date | Data da despesa |
| category | CharField(30) | admin, marketing, rent, salary, tax, tools, other |
| notes | TextField(null) | Observações |
| created_at | DateTime(auto) | Auto |

## Permissões (Django Groups)

| Grupo | Acesso |
|-------|--------|
| **Sem login** | Apenas visualizar motos (cliente) |
| **gerente** | CRUD completo de motos |
| **financeiro** | CRUD de motos + todo o /stock/* |

Usuário `mborges` adicionado ao grupo `financeiro` na migration.

## Rotas da API / Páginas

| URL | View | Descrição |
|-----|------|-----------|
| `/stock/` | StockDashboardView | Dashboard financeiro com cards |
| `/stock/motos/` | StockListView | Planilha de estoque |
| `/stock/motos/<pk>/` | StockDetailView | Custos detalhados de uma moto |
| `/stock/motos/<pk>/custos/` | StockCostUpdateView | Editar custos |
| `/stock/motos/<pk>/vender/` | SaleCreateView | Registrar venda |
| `/stock/motos/<pk>/ocultar/` | StockToggleHiddenView | Ocultar do site público |
| `/stock/motos/<pk>/exibir/` | StockToggleVisibleView | Reexibir no site |
| `/stock/despesas/` | ExpenseListView | Listar despesas extras |
| `/stock/despesas/nova/` | ExpenseCreateView | Nova despesa |
| `/stock/despesas/<pk>/editar/` | ExpenseUpdateView | Editar despesa |
| `/stock/despesas/<pk>/excluir/` | ExpenseDeleteView | Excluir despesa |

## Funcionalidades Implementadas

### Checklist Final

- [x] 00. Criar branch stock-control e estrutura inicial
- [x] 01. Modelos MotoStock e ExtraExpense + migrations
- [x] 02. Registrar app e configurar settings.py
- [x] 03. Decorator de permissão financeiro (`financeiro_required`)
- [x] 04. Base template com sidebar + navbar + toggle dark/light
- [x] 05. Dashboard com cards de resumo (estoque, vendas, lucro, despesas)
- [x] 06. Lista de estoque em formato planilha (spreadsheet)
- [x] 07. Detalhe de custos por moto (6 categorias)
- [x] 08. Formulário de custos (editar acquisition_cost, document_fees, etc.)
- [x] 09. Registrar venda com auto-cálculo de lucro
- [x] 10. CRUD completo de despesas extras (vinculadas ou gerais)
- [x] 11. Filtros no dashboard (mês, ano, status)
- [x] 12. Status sold/hidden: badge "VENDIDA" no site público
- [x] 13. Signal: criar MotoStock automaticamente ao cadastrar moto
- [x] 14. Toggle Ocultar/Exibir moto no site público
- [x] 15. Link "Controle" na navbar principal (só para financeiro)
- [x] 16. Motos ocultas excluídas da lista pública
- [x] 17. Grupos gerente/financeiro criados via data migration
- [x] 18. Testes de fluxo: cadastro, custos, venda, visibilidade

## Observações Técnicas

- O MotoStock é criado automaticamente via signal `post_save` do model Motos
- Views de custos e venda usam o pk do MotoStock na URL (não o pk da Motos)
- Tema dark/light integrado com o mesmo sistema do site (data-theme + localStorage)
- Formas de pagamento disponíveis: Pix, Dinheiro, Cartão créd/débito, Financiamento, Consórcio, Transferência, Outro
- Categorias de despesas: Administrativo, Marketing, Aluguel, Salários, Impostos, Ferramentas, Outros
