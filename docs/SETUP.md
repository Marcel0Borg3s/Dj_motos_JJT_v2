# 🛠️ Guia de Configuração (Setup)

Passo a passo para rodar o projeto JJT Motorcycles localmente.

---

## 📋 Pré-requisitos

| Ferramenta | Versão Mínima | Como Verificar |
|------------|--------------|----------------|
| Python | 3.12 | `python3 --version` |
| PostgreSQL | 16 | `psql --version` |
| pip | 24+ | `pip --version` |
| Git | 2.x | `git --version` |

---

## 🚀 Passo a Passo

### 1. Clone o Repositório

```bash
git clone https://github.com/Marcel0Borg3s/Dj_motos_JJT_v2.git
cd Dj_motos_JJT_v2
```

### 2. Crie o Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
# ou
venv\Scripts\activate      # Windows
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o Banco PostgreSQL

Entre no PostgreSQL e crie o banco:

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE motos;
CREATE USER postgres WITH PASSWORD 'Postgres@7596';
GRANT ALL PRIVILEGES ON DATABASE motos TO postgres;
\q
```

Se quiser alterar usuário/senha, edite em `app/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'motos',
        'USER': 'postgres',
        'PASSWORD': 'Postgres@7596',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Execute as Migrations

```bash
python manage.py migrate
```

### 6. Crie as Migrations Pendentes (se houver)

```bash
python manage.py makemigrations motos accounts stockcontrol
python manage.py migrate
```

### 7. Crie o Superusuário

```bash
python manage.py createsuperuser
```

**Credenciais padrão de desenvolvimento:**
- Usuário: `mborges`
- Senha: `7596`

### 8. Popule o Banco com Dados Iniciais

Os grupos de permissão (`gerente` e `financeiro`) são criados automaticamente via **data migration** ao rodar `migrate`.

Para adicionar o usuário ao grupo financeiro:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User, Group
user = User.objects.get(username='mborges')
group = Group.objects.get(name='financeiro')
user.groups.add(group)
user.save()
```

### 9. Configure a OpenRouter API (opcional)

Para usar a geração de descrição por IA, configure a chave da API em `app/settings.py`:

```python
OPENROUTER_API_KEY = 'sk-or-v1-sua-chave-aqui'
```

### 10. Crie o Diretório de Mídia

```bash
mkdir -p media/motos
```

### 11. Rode o Servidor

```bash
python manage.py runserver
```

Acesse: **http://localhost:8000**

---

## 📂 Estrutura de Diretórios de Mídia

```
media/
└── motos/               # Fotos enviadas pelas views
    ├─ foto1.jpg
    ├─ foto2.jpg
    └─ ...
```

---

## 🔄 Comandos Úteis do Django

| Comando | Descrição |
|---------|-----------|
| `python manage.py runserver` | Inicia servidor de desenvolvimento |
| `python manage.py makemigrations` | Cria migrations pendentes |
| `python manage.py migrate` | Aplica migrations ao banco |
| `python manage.py createsuperuser` | Cria superusuário admin |
| `python manage.py collectstatic` | Coleta arquivos estáticos |
| `python manage.py shell` | Shell interativo do Django |
| `python manage.py dbshell` | Shell direto do banco |

---

## 📦 Dependências (requirements.txt)

```text
asarPy==1.0.1
asgiref==3.9.1
Django==5.2.4
pillow==11.3.0
psycopg2-binary==2.9.10
sqlparse==0.5.3
```

---

## 🔧 Solução de Problemas

### Erro: `FATAL: password authentication failed for user "postgres"`

**Solução:** Altere a senha no PostgreSQL:
```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'Postgres@7596';"
```

### Erro: `django.db.utils.OperationalError: could not connect to server`

**Solução:** Verifique se o PostgreSQL está rodando:
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Erro: `No module named 'PIL'`

**Solução:** Instale o Pillow (pode precisar de system packages):
```bash
pip install pillow
# Se falhar no Linux:
sudo apt install python3-pil python3-pil.imagetk
```

### Erro: `relation "stockcontrol_extrapense" does not exist`

**Solução:** Execute as migrations novamente:
```bash
python manage.py migrate stockcontrol
```

### Tema Dark/Light não funciona?

O tema é salvo no `localStorage` do navegador. Limpe o cache do site ou abra uma aba anônima.

---

## 🌐 Deploy em Produção

### Opção 1: Render.com (já configurado)

O projeto tem branch `deploy_render` com configurações para deploy no Render.

### Opção 2: Servidor Linux

```bash
# Instale dependências de produção
pip install gunicorn

# Configure variáveis de ambiente
export DJANGO_SETTINGS_MODULE=app.settings
export SECRET_KEY="sua-chave-secreta-aqui"
export DEBUG=False

# Colete arquivos estáticos
python manage.py collectstatic

# Rode com Gunicorn
gunicorn app.wsgi:application --bind 0.0.0.0:8000
```

> **⚠️ Importante:** Em produção, nunca use `DEBUG=True`, nunca deixe `SECRET_KEY` no código, e troque a senha do banco.

---

## 🧪 Testes

```bash
# Rodar todos os testes
python manage.py test

# Rodar testes de um app específico
python manage.py test motos
python manage.py test stockcontrol

# Rodar com mais detalhes
python manage.py test -v 2
```
