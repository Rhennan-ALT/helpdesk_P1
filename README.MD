# Help Desk / Chamados — P1 (MVP)

Sistema de Help Desk em Django com cálculo automático de prazo de SLA
conforme a Prioridade e Categoria do chamado.

## Entidades

- **Equipe** — grupo de atendimento (ex: Suporte TI, Infraestrutura, RH)
- **Categoria** — classificação do problema (ex: Hardware, Software, Acesso)
- **Prioridade** — nível de urgência (ex: Baixa, Média, Alta, Crítica)
- **SLA** — horas limite de resolução para cada combinação Categoria + Prioridade
- **Chamado** — a solicitação em si, com status e prazo calculado automaticamente

## Como rodar

```bash
# 1. Criar e ativar um ambiente virtual
python -m venv venv
source venv/bin/activate     

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Gerar e aplicar as migrações
python manage.py makemigrations
python manage.py migrate

# 4. (Opcional) Popular Equipes, Categorias, Prioridades e SLAs de exemplo
python manage.py seed_dados

# 5. Criar um usuário administrador
python manage.py createsuperuser

# 6. Rodar o servidor
python manage.py runserver
```