# Help Desk

Projeto da disciplina Laboratório de Programação Full Stack, evoluído de um
MVP (P1) para um mini-SaaS (P2).

## Sumário

- [Funcionalidades](#funcionalidades)
- [Como o prazo do SLA funciona](#como-o-prazo-do-sla-funciona)
- [Papéis e permissões](#papéis-e-permissões)
- [Tecnologias](#tecnologias)
- [Como rodar](#como-rodar)
- [API REST](#api-rest)
- [Testes](#testes)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Roteiro de testes de isolamento](#roteiro-de-testes-de-isolamento-aula-14)
- [Documentação](#documentação)

## Funcionalidades

- **Multi-organização**: cada empresa tem seus próprios usuários, equipes,
  categorias, prioridades, SLAs e chamados. Uma organização nunca vê os dados
  de outra, nem pelas telas nem pela API.
- **Cadastro self-service**: quem se cadastra cria a sua organização, vira
  administrador dela e já recebe equipes, categorias, prioridades e SLAs iniciais.
- **Chamados com prazo automático**: o prazo é calculado pelo SLA da combinação
  categoria + prioridade e recalculado se uma delas mudar.
- **Painel de chamados** com busca, filtros por status e tipo, e filtro de atrasados.
- **Dashboard** com totais por status, chamados fora do prazo, distribuição por
  status e tipo, série mensal, ranking de equipes e categorias e filtro por período.
- **Exportação CSV** do relatório, respeitando a organização e o período filtrado.
- **Papéis de acesso** (administrador e operador), aplicados nas telas, na API e no dashboard.
- **API REST** com autenticação e as mesmas regras de isolamento e permissão das telas.
- **Interface responsiva** com barra lateral, que vira menu deslizante no celular.

## Como o prazo do SLA funciona

Cada SLA define quantas horas a organização tem para resolver um chamado de uma
categoria com uma prioridade (por exemplo, Hardware + Alta = 8 horas). Ao abrir
o chamado, o prazo é `data de abertura + horas do SLA`.

No painel, cada chamado mostra a situação do prazo:

| Situação | Quando | Cor |
|---|---|---|
| No prazo | consumiu menos de 75% do prazo | verde |
| Em risco | consumiu 75% ou mais e ainda não venceu | âmbar |
| Atrasado | passou do prazo e não foi concluído | vinho |
| Concluído | status fechado | cinza |
| Sem SLA | não há SLA para a combinação categoria + prioridade | cinza claro |

## Papéis e permissões

| | Administrador | Operador |
|---|---|---|
| Chamados | vê, edita e exclui todos da organização | vê e edita os que abriu ou pelos quais é responsável; não exclui |
| Equipes, categorias, prioridades e SLAs | cria, edita e exclui | sem acesso |
| API dos cadastros | leitura e escrita | somente leitura |
| Dashboard | completo, com série mensal, lista de atrasados e exportação CSV | totais, distribuições e rankings |

O papel fica no **Perfil** do usuário e pode ser alterado pelo Admin do Django
(Usuários → usuário → seção Perfil). O `is_staff` do Django só dá acesso ao `/admin/`;
quem decide o que o usuário faz no sistema é o papel.

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3.12, Django 6.1 |
| API | Django REST Framework |
| Banco de dados | PostgreSQL 16 (Docker Compose) |
| Front-end | Templates Django, Bootstrap 5, Bootstrap Icons, Chart.js |
| Configuração | python-dotenv (`.env`) |

## Como rodar

### Pré-requisitos

- Python 3.12 ou superior
- Docker Desktop (para o PostgreSQL)
- Git

### Passo a passo

```bash
# 1. Clonar o repositório
git clone https://github.com/Rhennan-ALT/helpdesk_P1.git
cd helpdesk_P1

# 2. Criar e ativar o ambiente virtual
python -m venv venv
source venv/Scripts/activate      # Windows (Git Bash)
# source venv/bin/activate        # Linux / macOS

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Criar o arquivo de configuração
cp .env.example .env
```

Gere uma `SECRET_KEY` e cole no `.env`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```bash
# 5. Subir o PostgreSQL
docker compose up -d

# 6. Criar as tabelas
python manage.py migrate

# 7. (Opcional) Dados de exemplo para uma organização
python manage.py seed_dados

# 8. Criar o administrador
python manage.py createsuperuser

# 9. Rodar
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`. Para usar o sistema, crie uma organização
pela tela de cadastro, ou, no Admin, dê ao superusuário um Perfil com o papel
Administrador. Usuários sem Perfil recebem "Sem acesso" nas telas do sistema.

### Variáveis de ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave secreta do Django | — (obrigatória) |
| `DEBUG` | Modo de desenvolvimento | `True` |
| `ALLOWED_HOSTS` | Hosts aceitos, separados por vírgula | `127.0.0.1,localhost` |
| `DB_ENGINE` | `postgres` ou `sqlite` (só para exportar dados antigos) | `postgres` |
| `POSTGRES_DB` | Nome do banco | `helpdesk` |
| `POSTGRES_USER` | Usuário do banco | `helpdesk` |
| `POSTGRES_PASSWORD` | Senha do banco | `helpdesk` |
| `POSTGRES_HOST` | Host do banco | `localhost` |
| `POSTGRES_PORT` | Porta do banco | `5432` |

O `.env` não vai para o Git; o modelo versionado é o `.env.example`.

### Comandos úteis

| Comando | O que faz |
|---|---|
| `python manage.py seed_dados --org "Nome"` | Cria (ou completa) uma organização com dados de exemplo |
| `python manage.py changepassword <usuário>` | Troca a senha de um usuário |
| `docker compose stop` | Para o banco, mantendo os dados |
| `docker compose down -v` | Apaga o container e os dados (banco zerado) |

## API REST

Base: `/api/`. A autenticação é por sessão: entre no sistema ou em
`/api-auth/login/` para usar a Browsable API no navegador. Sem login, a API
responde 403. Todos os endpoints retornam só os dados da organização do usuário.

| Endpoint | Métodos | Observação |
|---|---|---|
| `/api/chamados/` | GET, POST | Operador lista só os próprios chamados |
| `/api/chamados/<id>/` | GET, PUT, PATCH, DELETE | DELETE só para administrador |
| `/api/equipes/` e `/api/equipes/<id>/` | GET, POST, PUT, PATCH, DELETE | Escrita só para administrador |
| `/api/categorias/` e `/api/categorias/<id>/` | GET, POST, PUT, PATCH, DELETE | Escrita só para administrador |
| `/api/prioridades/` e `/api/prioridades/<id>/` | GET, POST, PUT, PATCH, DELETE | Escrita só para administrador |
| `/api/slas/` e `/api/slas/<id>/` | GET, POST, PUT, PATCH, DELETE | Escrita só para administrador |
| `/api/dashboard/` | GET | Métricas do dashboard; aceita `?inicio=AAAA-MM-DD&fim=AAAA-MM-DD` |

Excluir uma equipe, categoria ou prioridade que ainda tem chamados retorna `409 Conflict`.

## Testes

```bash
python manage.py test core.tests
```

Os testes do dashboard (`core/tests/test_dashboard.py`) cobrem os totais por
organização, o filtro de período, o dashboard vazio, as permissões por papel,
a exportação CSV, a API e, com `assertNumQueries`, garantem que o número de
consultas não cresce com a quantidade de chamados. O usuário do banco precisa
da permissão `CREATEDB`, que o container do Docker já concede.

## Estrutura do projeto

```
helpdesk_P1/
├── helpdesk/                 # configurações do projeto (settings, urls)
├── core/
│   ├── models.py             # Organização, Perfil, Equipe, Categoria, Prioridade, SLA, Chamado
│   ├── views.py              # telas (painel, chamados, cadastros, dashboard, CSV)
│   ├── views_api.py          # endpoints da API
│   ├── serializers.py        # serializers do DRF
│   ├── forms.py              # formulários com selects filtrados pela organização
│   ├── dashboard.py          # métricas do dashboard (aggregate / annotate)
│   ├── organizacao.py        # org_atual(request)
│   ├── permissoes.py         # papel_requerido e permissões por papel
│   ├── dados_iniciais.py     # dados criados para cada nova organização
│   ├── management/commands/  # seed_dados
│   ├── migrations/
│   ├── templates/            # base com barra lateral, telas e páginas de entrada
│   ├── static/core/css/      # CSS dividido por área (layout, sidebar, sla, dashboard...)
│   ├── static/core/js/       # menu do celular e gráficos do dashboard
│   └── tests/                # testes automatizados
├── docs/                     # wireframes da P1 (Figma)
├── docker-compose.yml        # PostgreSQL
├── .env.example              # modelo das variáveis de ambiente
├── BACKLOG.md
├── MELHORIAS_P1.md
└── requirements.txt
```

## Roteiro de testes de isolamento

Executado com dois usuários de organizações diferentes: `test` na
**Organização padrão** (A) e `bruno` na **Org B**.

| Cenário | Resultado esperado | Resultado |
|---------|--------------------|-----------|
| Usuário da A abre o painel e as listas | Vê só os registros da A | ✅ |
| Usuário da A abre `/chamados/<id-da-B>/` | 404 | ✅ |
| Usuário da A abre `/equipes/<id-da-B>/editar/` | 404 | ✅ |
| Usuário da A cria um chamado | Gravado na A e invisível para a B | ✅ |
| Selects do formulário de chamado na A | Só equipes, categorias, prioridades e responsáveis da A | ✅ |
| Usuário da A cadastra equipe com nome que só existe na B | Permitido | ✅ |
| Usuário da A cadastra equipe com nome repetido na A | Erro de validação | ✅ |
| Usuário da A acessa `/api/chamados/<id-da-B>/` | 404 | ✅ |
| Usuário da B repete os cenários com dados da A | Mesmo comportamento | ✅ |

## Documentação

- [MELHORIAS_P1.md](MELHORIAS_P1.md): problemas encontrados no MVP e como foram resolvidos
- [BACKLOG.md](BACKLOG.md): tarefas da P2 organizadas pelos quatro pilares

---
