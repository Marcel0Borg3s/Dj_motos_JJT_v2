# 🏗️ Arquitetura do Sistema

Documento técnico com a arquitetura do JJT Motorcycles — modelos de dados, fluxos, design system e decisões de arquitetura.

---

## 📐 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    DJANGO 5.2 — app                         │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │  motos   │  │ accounts │  │      stockcontrol         │  │
│  │ (catálogo)│  │   (auth) │  │  (estoque e custos)      │  │
│  └────┬─────┘  └────┬─────┘  └───────────┬──────────────┘  │
│       │              │                    │                  │
│       └──────────────┴────────────────────┘                  │
│                          │                                    │
│                    ┌─────┴──────┐                             │
│                    │ PostgreSQL │                             │
│                    │  (motos)   │                             │
│                    └────────────┘                             │
│                                                              │
│  ┌──────────────────────────────────────────────┐            │
│  │           OpenRouter API (NVIDIA)            │            │
│  │        Geração de descrições por IA          │            │
│  └──────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧱 Modelos de Dados

### 1. App `motos` — Catálogo

#### Brand (Marca)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | AutoField (PK) | Identificador |
| name | CharField(100) | Nome da marca (Yamaha, Honda, BMW...) |

Criado automaticamente via formulário — o usuário digita o nome da marca e o sistema busca ou cria o registro.

#### Motos (Moto)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | AutoField (PK) | Identificador |
| model | CharField(200) | Modelo da moto |
| brand | FK → Brand | Marca (on_delete=PROTECT) |
| factor_year | Integer(null) | Ano de fabricação |
| model_year | Integer(null) | Ano do modelo |
| plate | CharField(10,null) | Placa |
| value | FloatField(null) | Valor de anúncio (R$) |
| bio | TextField(null) | Descrição técnica |
| photo..photo6 | ImageField | Até 6 fotos |

#### MotoInventory (Inventário)
Snapshot periódico do estoque. Criado automaticamente via signals ao salvar/deletar uma moto.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| motos_count | Integer | Total de motos |
| motos_value | Float | Valor total do estoque |
| created_at | DateTime(auto) | Timestamp |

---

### 2. App `stockcontrol` — Estoque e Custos

#### MotoStock (1:1 com Motos)
Controle financeiro individual de cada moto. **Criado automaticamente** via signal `post_save` do model Motos.

**Campos de Custo (6 categorias):**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| acquisition_cost | Decimal(12,2) | Valor de entrada/compra |
| document_fees | Decimal(10,2) | Taxas de documento |
| transport_cost | Decimal(10,2) | Frete/transporte |
| maintenance_cost | Decimal(10,2) | Manutenção/preparação |
| fines_cost | Decimal(10,2) | Multas |
| other_costs | Decimal(10,2) | Outras despesas |

**Campos de Venda:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| sale_value | Decimal(12,2,null) | Valor da venda |
| sale_status | CharField(20) | available / sold / hidden |
| sale_date | Date(null) | Data da venda |
| buyer_name | CharField(200) | Nome do comprador |
| buyer_document | CharField(20) | CPF/CNPJ |
| payment_method | CharField(50) | Forma de pagamento |

**Campos de Exibição:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| show_price | Boolean(default=True) | Se False, mostra "Consulte-nos" |

**Propriedades Calculadas:**
| Propriedade | Fórmula |
|-------------|---------|
| `total_cost` | Soma das 6 categorias de custo |
| `profit` | sale_value - total_cost |
| `profit_margin` | (profit / total_cost) × 100 |
| `is_sold` | sale_status == 'sold' |
| `is_hidden` | sale_status == 'hidden' |

#### ExtraExpense (Despesa Extra)
Despesas operacionais não previstas no MotoStock.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| moto | FK → Motos(null) | Vinculada a uma moto ou geral |
| description | CharField(300) | Descrição |
| amount | Decimal(12,2) | Valor |
| date | Date | Data |
| category | CharField(30) | admin, marketing, rent, salary, tax, tools, other |
| notes | TextField(null) | Observações |

---

## 🔗 Fluxos Principais

### Fluxo 1: Cadastro de Moto → Estoque

```
Usuário preenche form
       │
       ▼
NewMotoCreateView
       │
       ▼
Motos.objects.create(...)   ← Cria a moto
       │
       ▼
Signal: criar_stock_ao_cadastrar_moto
       │
       ▼
MotoStock.objects.get_or_create(moto=instance)   ← Cria registro de estoque
       │
       ▼
Signal: moto_post_save (MotoInventory)
       │
       ▼
MotoInventory.objects.create(...)   ← Atualiza snapshot
```

### Fluxo 2: Site Público (Lista de Motos)

```
Visitante acessa /motos/
       │
       ▼
MotosListView.get_queryset()
       │
       ├── Anota stock_status e stock_show_price via Subquery do MotoStock
       ├── Exclui motos com sale_status='hidden'
       ├── Filtra por search term (se houver)
       └── Ordena por model
       │
       ▼
Template motos.html
       │
       ├── Grid de cards com foto, marca, modelo, ano
       ├── Badge "VENDIDA" se stock_status == 'sold'
       └── Preço ou "Consulte-nos" conforme stock_show_price
```

### Fluxo 3: Geração de Descrição por IA

```
Usuário clica "Gerar Descrição" (JS)
       │
       ▼
fetch POST /motos/gerar-descricao/
       │
       ▼
generate_description(request)
       │
       ├── Monta prompt com marca, modelo, anos
       ├── Envia para OpenRouter API (NVIDIA Nemotron)
       └── Retorna JSON com description
       │
       ▼
JS preenche campo bio no formulário
```

### Fluxo 4: Venda de Moto

```
Usuário do grupo financeiro acessa /stock/motos/<pk>/vender/
       │
       ▼
SaleCreateView (UpdateView)
       │
       ├── Exibe form com valor, comprador, documento, pagamento, data
       ├── Mostra custo total da moto
       │
       ▼
form_valid()
       │
       ├── Seta sale_status = 'sold'
       ├── Seta sale_date = hoje (se vazio)
       └── Calcula profit automaticamente (propriedade)
       │
       ▼
Redireciona para detalhe com mensagem de lucro
```

---

## 🎨 Design System (Ferrari)

O visual do projeto é baseado no **Ferrari Design System** — elegante, escuro, com cantos vivos e tipografia precisa.

### Tokens Principais (`ferrari.css`)

```css
:root {
  --ferrari-red:       #DA291C;  /* Vermelho Ferrari */
  --near-black:        #181818;  /* Fundo escuro */
  --dark-surface:      #303030;  /* Cards */
  --absolute-black:    #000000;  /* Navbar, footer */

  /* Tipografia */
  --font-heading:      'DM Sans', sans-serif;
  --font-body:         'Barlow Condensed', sans-serif;

  --radius: 2px;  /* Cantos vivos Ferrari */
}
```

### Tema Dark/Light

O tema é controlado por:
1. **CSS Variables** — `:root` para dark, `[data-theme="light"]` para light
2. **localStorage** — tema salvo no navegador
3. **Anti-flash** — script inline no `<head>` que aplica o tema antes do CSS carregar

### Responsividade

- **Desktop (>768px)**: Layout normal com sidebar
- **Tablet (480-768px)**: Sidebar recolhida, cards em 2 colunas
- **Mobile (<480px)**: Cards em 1 coluna, tabela com fonte menor

---

## 🔐 Sistema de Permissões

```
Usuário autenticado
       │
       ├── Superuser → Acesso total (inclusive financeiro)
       │
       ├── Grupo "financeiro" → Tudo que gerente faz + /stock/*
       │     └── Verificado por: @financeiro_required
       │
       ├── Grupo "gerente" → CRUD de motos
       │     └── Verificado por: @login_required
       │
       └── Visitante (sem login) → Apenas /motos/ e /motos/<pk>/
```

---

## ⚡ Sinais (Signals)

### App `motos` (`motos/signals.py`)

| Signal | Ação |
|--------|------|
| `post_save(Motos)` | Atualiza MotoInventory |
| `post_delete(Motos)` | Atualiza MotoInventory |
| `pre_save(Motos)` | Define bio padrão se vazio |

### App `stockcontrol` (`stockcontrol/signals.py`)

| Signal | Ação |
|--------|------|
| `post_save(Motos)` se `created=True` | Cria MotoStock automaticamente |

---

## 📁 Separação de Responsabilidades

```
motos/                    → Catálogo público e CRUD de motos
accounts/                 → Autenticação (login, register, logout)
stockcontrol/             → Controle financeiro, estoque, custos, vendas
```

**Por que `stockcontrol` é separado?**
- Clareza: cada app tem responsabilidade única
- Permissões: estoque requer grupo `financeiro`, catálogo é público
- Manutenção: alterações no financeiro não afetam o site público
- Reuso: o módulo de estoque poderia ser extraído para outro projeto

---

## 📡 APIs Externas

### OpenRouter API (Geração de Descrição)

- **Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Modelo**: `nvidia/nemotron-3-nano-30b-a3b:free` (gratuito)
- **Autenticação**: Bearer token via `OPENROUTER_API_KEY`
- **Uso**: Geração de descrições técnicas de motos no formulário de cadastro
- **Timeout**: 30 segundos

---

## 🗄️ Banco de Dados

| Informação | Valor |
|-----------|-------|
| Engine | PostgreSQL |
| Nome | `motos` |
| Host | localhost:5432 |
| User | postgres |

### Migrations

| App | Migrations |
|-----|-----------|
| motos | 0001_initial (tabelas Brand, Motos, MotoInventory) |
| accounts | (nenhuma — usa auth padrão do Django) |
| stockcontrol | 0001_initial (MotoStock, ExtraExpense) |
| stockcontrol | 0002_criar_grupos (grupos gerente + financeiro) |
| stockcontrol | 0003_motostock_show_price (campo show_price) |

---

## 🧠 Decisões de Arquitetura

| Decisão | Motivo |
|---------|--------|
| **CSS puro sem frameworks** | Controle total sobre cada pixel, payload reduzido, sem conflitos |
| **Brand como text input** | Usuário digita a marca, sistema busca/cria — evita selects gigantes |
| **MotoStock via signal** | Garante que toda moto tenha registro de estoque automaticamente |
| **6 categorias de custo em colunas** vs tabela separada | Simplicidade: cada moto tem no máximo 6 custos, não justifica normalizar |
| **FloatField para value na Motos** vs Decimal | Legado — motos existia antes do stockcontrol. Novo código usa Decimal |
| **financeiro_required** vs @login_required | Garantia extra de que só usuários autorizados acessam dados financeiros |
| **show_price no MotoStock** vs na Motos | Faz sentido financeiro controlar exibição de preço, não o catálogo |
