from django.core.management.base import BaseCommand
from core.models import SLA, Categoria, Equipe, Prioridade


class Command(BaseCommand):
    help = 'Popula o banco com Equipes, Categorias, Prioridades e SLAs de exemplo.'

    def handle(self, *args, **options):
        equipes = ['Suporte TI', 'Infraestrutura', 'RH']
        for nome in equipes:
            Equipe.objects.get_or_create(nome=nome)

        categorias = ['Hardware', 'Software', 'Acesso']
        for nome in categorias:
            Categoria.objects.get_or_create(nome=nome)

        prioridades = [
            ('Crítica', 1),
            ('Alta', 2),
            ('Média', 3),
            ('Baixa', 4),
        ]
        for nome, ordem in prioridades:
            Prioridade.objects.get_or_create(nome=nome, defaults={'ordem': ordem})

        horas_por_prioridade = {
            'Crítica': 4,
            'Alta': 8,
            'Média': 24,
            'Baixa': 72,
        }
        criados = 0

        for categoria in Categoria.objects.all():
            for prioridade in Prioridade.objects.all():
                _, criado = SLA.objects.get_or_create(
                    categoria=categoria,
                    prioridade=prioridade,
                    defaults={'horas': horas_por_prioridade.get(prioridade.nome, 24)},
                )
                criados += int(criado)

        self.stdout.write(self.style.SUCCESS(
            f'Dados iniciais criados: {len(equipes)} equipes, {len(categorias)} categorias, '
            f'{len(prioridades)} prioridades e {criados} novos SLAs.'
        ))
