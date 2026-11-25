# Backlog da P2 — Help Desk como Mini-SaaS

## Pilar 1 — API REST (DRF) 
- [x] Instalar DRF e registrar em `INSTALLED_APPS`
- [x] Serializers de Equipe, Categoria, Prioridade, SLA e Chamado (fields explícitos, sem `__all__`)
- [x] Views generics (ListCreate / RetrieveUpdateDestroy) e `urls_api.py` com prefixo `/api/`
- [x] Autenticação por sessão + `IsAuthenticated` como padrão
- [x] Exclusão protegida devolvendo 409
- [x] Campo `tipo` exposto no serializer
- [x] API testada pela Browsable API (navegador) e com curl
- [x] Filtrar toda a API pela organização do usuário
- [x] Permissões por papel nos endpoints de cadastro

## Pilar 2 — Multi-organização 
- [x] Model `Organizacao` e base abstrata `DaOrganizacao`
- [x] FK de organização em Equipe, Categoria, Prioridade, SLA e Chamado
- [x] Migração em 3 etapas (FK nula → organização padrão via `RunPython` → FK obrigatória)
- [x] `Perfil` (usuário → organização) e cadastro no Admin
- [x] Unicidade por organização (`nome` de Equipe/Categoria/Prioridade, combinação do SLA)
- [x] `org_atual(request)`, filtro em todas as views, `get_object_or_404` com organização
- [x] Selects dos formulários filtrados pela organização (inclusive Responsável)
- [x] Roteiro de testes de isolamento com dois usuários de organizações diferentes

## Pilar 3 — Perfis de acesso 
- [x] Campo `papel` (admin / operador) no `Perfil`
- [x] Restringir telas e endpoints de cadastro ao papel admin
- [x] Definir o comportamento do superusuário sem Perfil: bloqueado (403) até ganhar um Perfil no Admin
- [x] Operador vê e edita só os próprios chamados; exclusão de chamados só para admin
- [x] Quem cria a organização pelo cadastro vira admin; usuários existentes com `is_staff` viraram admin

## Pilar 4 — Dashboard 
Perguntas do dono do help desk:
1. Quantos chamados estão abertos, em atendimento e concluídos? → **KPIs / distribuição por status**
2. Quais chamados estouraram o SLA? → **KPI de atrasados + lista**
3. Qual tipo de chamado (incidente, requisição, dúvida) predomina? → **distribuição por tipo**
4. Quais equipes/categorias recebem mais chamados? → **ranking**
5. Como evolui o volume de chamados por mês? → **série temporal**

- [x] `core/dashboard.py` com as métricas (aggregate/annotate), sempre partindo da organização
- [x] Filtro por período validado com `PeriodoForm`
- [x] Tela com cartões, tabela e gráfico Chart.js (`json_script`)
- [x] Exportação CSV e endpoint `/api/dashboard/`
- [x] Índice em Chamado (`organizacao`, `data_criacao`)
- [x] Série por mês, lista de atrasados e CSV só para o papel admin
- [x] Testes das métricas e `assertNumQueries` contra N+1 (`core/tests/test_dashboard.py`)

## Infra
- [x] Migrar de SQLite para PostgreSQL, configurações via `.env`
