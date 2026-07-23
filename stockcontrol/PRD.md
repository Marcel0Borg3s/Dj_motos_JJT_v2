# PRD — Controle de Estoque e Lucratividade (FASE 2)

## Objetivo
Sistema integrado ao projeto JJT Motorcycles para controle financeiro de estoque,
custos por moto, registro de vendas, despesas operacionais e dashboard de
lucratividade. Acesso exclusivo para usuários do grupo **financeiro**.

## Arquitetura

```
stockcontrol/                  # Novo app separado do motos/
├── models.py                  # MotoStock, ExtraExpense
├── views.py                   # Dashboard, CRUD views
├── urls.py                    # Rotas /stock/*
├── forms.py                   # Forms para custos, vendas, despesas
├── decorators.py              # Decorador de permissão financeiro
├── admin.py                   # Registro admin
├── templates/stockcontrol/
│   ├── base_stock.html        # Base com sidebar + navbar
│   ├── dashboard.html         # Dashboard principal
│   ├── stock_list.html        # Lista de motos com custos
│   ├── stock_detail.html      # Custos detalhados de uma moto
│   ├── expense_form.html      # Adicionar/editar despesa extra
│   └── sale_form.html         # Registrar venda
└── tests.py                   # Testes
```

## Modelos de Dados

### MotoStock (1:1 com Motos)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| moto | OneToOneField(Motos) | Vínculo com a moto |
| acquisition_cost | Decimal | Valor de entrada (compra) |
| document_fees | Decimal | Despesas de documento |
| transport_cost | Decimal | Transferência/transporte |
| maintenance_cost | Decimal | Manutenção/preparação |
| fines_cost | Decimal | Multas |
| other_costs | Decimal | Outras despesas não previstas |
| sale_value | Decimal (null) | Valor da venda (preenche ao vender) |
| sale_status | CharField | available, sold, hidden |
| sale_date | Date (null) | Data da venda |
| buyer_name | CharField | Nome do comprador |
| buyer_document | CharField | CPF/CNPJ |
| payment_method | CharField | Forma de pagamento |
| additional_notes | TextField | Observações |
| created_at | DateTime | Auto |
| updated_at | DateTime | Auto |

**Propriedades calculadas:** `total_cost`, `profit`, `profit_margin`

### ExtraExpense
| Campo | Tipo | Descrição |
|-------|------|-----------|
| moto | FK(Motos, null) | Vinculado a uma moto ou geral |
| description | CharField | Descrição da despesa |
| amount | Decimal | Valor |
| date | Date | Data |
| category | CharField | Categoria (administrativo, marketing, etc.) |
| notes | TextField (null) | Observações |
| created_at | DateTime | Auto |

## Permissões (Django Groups)

| Grupo | Acesso |
|-------|--------|
| **Sem login** | Apenas visualizar motos (cliente) |
| **gerente** | CRUD completo de motos (já existe) |
| **financeiro** | CRUD de motos + todo o /stock/* |

## Páginas

### 1. Dashboard `/stock/`
- Sidebar com navegação
- Cards de resumo: total motos, valor em estoque, lucro potencial, última venda
- Tabela de motos com custos, margem, status
- Filtros: mês, período, status

### 2. Custos por Moto `/stock/<pk>/`
- Todos os custos da moto em grid
- Total calculado
- Botões: Editar custos, Registrar venda, Despesa extra

### 3. Registrar Venda `/stock/<pk>/vender/`
- Formulário com valor, comprador, documento, forma de pagamento
- Auto-cálculo do lucro
- Altera status para 'sold'

### 4. Despesa Extra `/stock/despesa/nova/` e `/stock/<pk>/despesa/`
- Vincular despesa a uma moto ou geral
- Categoria, valor, descrição

### 5. Lista de Estoque `/stock/motos/`
- Tabela completa tipo planilha
- Colunas: Moto, Custo Total, Valor Venda, Margem, Status
- Ações por linha: Detalhes, Editar, Vender

## Funcionalidades por Tarefa

- [x] 00. Criar branch stock-control e estrutura inicial
- [ ] 01. Modelos MotoStock e ExtraExpense + migrations
- [ ] 02. Registrar app e configurar settings.py
- [ ] 03. Decorator de permissão financeiro
- [ ] 04. Base template com sidebar
- [ ] 05. Dashboard com cards e tabela
- [ ] 06. Lista de estoque (planilha)
- [ ] 07. Detalhe de custos por moto
- [ ] 08. Formulário de custos (editar)
- [ ] 09. Registrar venda
- [ ] 10. Despesas extras
- [ ] 11. Filtros no dashboard
- [ ] 12. Status sold/hidden para cliente
- [ ] 13. Criar grupos gerente/financeiro via migration
- [ ] 14. Testar todas as funcionalidades
