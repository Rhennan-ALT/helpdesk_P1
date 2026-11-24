from .models import SLA, Categoria, Equipe, Prioridade

EQUIPES = ['Suporte TI', 'Infraestrutura', 'RH']
CATEGORIAS = ['Hardware', 'Software', 'Acesso']
PRIORIDADES = [('Crítica', 1), ('Alta', 2), ('Média', 3), ('Baixa', 4)]
HORAS_POR_PRIORIDADE = {'Crítica': 4, 'Alta': 8, 'Média': 24, 'Baixa': 72}


def criar_dados_iniciais(org):
    for nome in EQUIPES:
        Equipe.objects.get_or_create(organizacao=org, nome=nome)

    for nome in CATEGORIAS:
        Categoria.objects.get_or_create(organizacao=org, nome=nome)

    for nome, ordem in PRIORIDADES:
        Prioridade.objects.get_or_create(organizacao=org, nome=nome, defaults={'ordem': ordem})

    novos_slas = 0
    for categoria in Categoria.objects.filter(organizacao=org):
        for prioridade in Prioridade.objects.filter(organizacao=org):
            _, criado = SLA.objects.get_or_create(
                organizacao=org,
                categoria=categoria,
                prioridade=prioridade,
                defaults={'horas': HORAS_POR_PRIORIDADE.get(prioridade.nome, 24)},
            )
            novos_slas += int(criado)
    return novos_slas
