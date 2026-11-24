from django.core.management.base import BaseCommand

from core.dados_iniciais import CATEGORIAS, EQUIPES, PRIORIDADES, criar_dados_iniciais
from core.models import Organizacao


class Command(BaseCommand):
    help = 'Popula uma organização com Equipes, Categorias, Prioridades e SLAs de exemplo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--org', default='Organização padrão',
            help='Nome da organização (é criada se não existir).',
        )

    def handle(self, *args, **options):
        org, criada = Organizacao.objects.get_or_create(nome=options['org'])
        novos_slas = criar_dados_iniciais(org)

        self.stdout.write(self.style.SUCCESS(
            f'{"Organização criada" if criada else "Organização"}: {org}. '
            f'{len(EQUIPES)} equipes, {len(CATEGORIAS)} categorias, '
            f'{len(PRIORIDADES)} prioridades e {novos_slas} novos SLAs.'
        ))
