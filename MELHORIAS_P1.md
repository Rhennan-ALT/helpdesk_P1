# Melhorias da P1

Revisão do MVP

| # | Problema encontrado | Onde | Como foi resolvido |
|---|---------------------|------|--------------------|
| 1 | **API aberta sem login**: faltava `REST_FRAMEWORK` no settings e o padrão do DRF é permitir tudo; qualquer pessoa podia criar e apagar registros. O campo `tipo` também não aparecia na API. | `settings.py`, `serializers.py` | `IsAuthenticated` como padrão e `tipo` no `ChamadoSerializer`. |
| 2 | **Erro 500 no painel**: o filtro "Somente atrasados" transformava a consulta em lista e quebrava quando combinado com tipo ou busca. | `views.painel` | `ChamadoQuerySet.atrasados()` filtra no banco; o mesmo filtro é usado no dashboard. |
| 3 | **Prazo do SLA não era recalculado** ao trocar a categoria ou a prioridade de um chamado. | `Chamado.save()` | O prazo é recalculado sempre que categoria ou prioridade mudam. |
| 4 | **Regra do SLA mínimo só no formulário**: a tela recusava 0 hora, mas a API e o Admin aceitavam. | `forms.SLAForm` | Virou `MinValueValidator(1)` no model (migração `0003`), valendo em todos os lugares. |
| 5 | **Erro 500 ao excluir** Equipe, Categoria ou Prioridade com chamados vinculados. | `views.*DeleteView` | Mensagem explicando o motivo e volta para a lista. |
| 6 | **Configuração presa no código**: banco SQLite fixo e `SECRET_KEY` no `settings.py`. | `settings.py` | PostgreSQL via Docker e configurações no `.env` (fora do Git). |
| 7 | **Permissões frágeis**: qualquer usuário logado editava os cadastros, e o select de Responsável listava todos os usuários do sistema. | `views.py`, `forms.py` | Organizações (Aula 14) e papéis admin/operador (perfis de acesso). |
