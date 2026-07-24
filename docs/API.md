# 🧭 Rotas e Endpoints

Referência completa de todas as URLs do sistema JJT Motorcycles.

---

## 🌐 Site Público (Sem Autenticação)

| URL | View | Descrição |
|-----|------|-----------|
| `/` | — | Redireciona para `/motos/` |
| `/motos/` | `MotosListView` | Lista com grid de motos + busca |
| `/motos/<pk>/` | `MotoDetailView` | Detalhes + carrossel de fotos |

---

## 🔐 Autenticação

| URL | View | Descrição |
|-----|------|-----------|
| `/login/` | `login_view` | Login |
| `/logout/` | `logout_view` | Logout |
| `/register/` | `register_view` | Registro de novo usuário |

---

## 👤 Autenticado (Grupo gerente ou financeiro)

| URL | View | Descrição |
|-----|------|-----------|
| `/admin/` | Django Admin | Painel admin padrão do Django |
| `/new_moto/` | `NewMotoCreateView` | Cadastrar nova moto (com fotos) |
| `/motos/<pk>/update/` | `MotoUpdateView` | Editar dados da moto |
| `/motos/<pk>/delete/` | `MotoDeleteView` | Excluir moto (com confirmação) |
| `/motos/gerar-descricao/` | `generate_description` | API: gera descrição por IA (POST) |

---

## 💰 Controle de Estoque (Grupo financeiro apenas)

Todas prefixadas com `/stock/` e protegidas pelo decorator `@financeiro_required`.

### Dashboard

| URL | View | Descrição |
|-----|------|-----------|
| `/stock/` | `StockDashboardView` | Dashboard com cards, gráficos e filtros |

### Estoque

| URL | View | Descrição |
|-----|------|-----------|
| `/stock/motos/` | `StockListView` | Planilha de estoque com filtro por status |
| `/stock/motos/<pk>/` | `StockDetailView` | Custos detalhados de uma moto |
| `/stock/motos/<pk>/custos/` | `StockCostUpdateView` | Editar custos (6 categorias) |
| `/stock/motos/<pk>/vender/` | `SaleCreateView` | Registrar venda |
| `/stock/motos/<pk>/ocultar/` | `StockToggleHiddenView` | Ocultar do site público |
| `/stock/motos/<pk>/exibir/` | `StockToggleVisibleView` | Reexibir no site |
| `/stock/motos/<pk>/preco/` | `StockTogglePriceView` | Alternar show_price |

### Despesas Extras

| URL | View | Descrição |
|-----|------|-----------|
| `/stock/despesas/` | `ExpenseListView` | Lista de despesas (paginação) |
| `/stock/despesas/nova/` | `ExpenseCreateView` | Nova despesa |
| `/stock/despesas/<pk>/editar/` | `ExpenseUpdateView` | Editar despesa |
| `/stock/despesas/<pk>/excluir/` | `ExpenseDeleteView` | Excluir despesa |

---

## 📋 Resumo por Funcionalidade

| Funcionalidade | URL | Requer Login | Requer Grupo |
|---------------|-----|:---:|:---:|
| Listar motos | `/motos/` | — | — |
| Detalhe da moto | `/motos/<pk>/` | — | — |
| Cadastrar moto | `/new_moto/` | ✅ | gerente+ |
| Editar moto | `/motos/<pk>/update/` | ✅ | gerente+ |
| Deletar moto | `/motos/<pk>/delete/` | ✅ | gerente+ |
| Gerar descrição IA | `/motos/gerar-descricao/` | ✅ | gerente+ |
| Dashboard estoque | `/stock/` | ✅ | financeiro |
| Planilha estoque | `/stock/motos/` | ✅ | financeiro |
| Custos detalhados | `/stock/motos/<pk>/` | ✅ | financeiro |
| Editar custos | `/stock/motos/<pk>/custos/` | ✅ | financeiro |
| Registrar venda | `/stock/motos/<pk>/vender/` | ✅ | financeiro |
| Ocultar/exibir | `/stock/motos/<pk>/ocultar/` | ✅ | financeiro |
| Toggle preço | `/stock/motos/<pk>/preco/` | ✅ | financeiro |
| Despesas (CRUD) | `/stock/despesas/*` | ✅ | financeiro |
| Admin Django | `/admin/` | ✅ | superuser |
| Login/Logout | `/login/`, `/logout/` | — | — |
| Registrar | `/register/` | — | — |

---

## 🔌 API de Descrição por IA

**Endpoint:** `POST /motos/gerar-descricao/`

**Headers:**
```
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
  "brand": "Yamaha",
  "model": "MT-07",
  "factor_year": "2024",
  "model_year": "2025"
}
```

**Response (200):**
```json
{
  "description": "A Yamaha MT-07 é uma moto naked que combina desempenho... \
  Com motor de 689cc e impressionantes 73,4 hp, oferece... \
  Entre em contato para mais informações!"
}
```

**Response (Erro):**
```json
{
  "error": "Erro HTTP 401: ..."
}
```
