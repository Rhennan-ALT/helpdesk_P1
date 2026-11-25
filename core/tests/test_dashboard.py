import csv
import io
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core import dashboard
from core.dados_iniciais import criar_dados_iniciais
from core.models import Categoria, Chamado, Equipe, Organizacao, Perfil, Prioridade


def novo_chamado(org, usuario, **extra):
    dados = dict(
        organizacao=org, solicitante=usuario, titulo='t', descricao='d',
        equipe=Equipe.objects.filter(organizacao=org).order_by('nome').first(),
        categoria=Categoria.objects.filter(organizacao=org).order_by('nome').first(),
        prioridade=Prioridade.objects.filter(organizacao=org).order_by('ordem').first(),
    )
    dados.update(extra)
    return Chamado.objects.create(**dados)


class DashboardBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org_a = Organizacao.objects.create(nome='Org A')
        cls.org_b = Organizacao.objects.create(nome='Org B')
        criar_dados_iniciais(cls.org_a)
        criar_dados_iniciais(cls.org_b)
        cls.admin_a = User.objects.create_user('admin_a', password='x')
        cls.operador_a = User.objects.create_user('operador_a', password='x')
        cls.admin_b = User.objects.create_user('admin_b', password='x')
        Perfil.objects.create(usuario=cls.admin_a, organizacao=cls.org_a, papel=Perfil.PAPEL_ADMIN)
        Perfil.objects.create(usuario=cls.operador_a, organizacao=cls.org_a)
        Perfil.objects.create(usuario=cls.admin_b, organizacao=cls.org_b, papel=Perfil.PAPEL_ADMIN)

        novo_chamado(cls.org_a, cls.admin_a, titulo='A1')
        novo_chamado(cls.org_a, cls.admin_a, titulo='A2', status=Chamado.STATUS_ANDAMENTO)
        novo_chamado(cls.org_a, cls.admin_a, titulo='A3', status=Chamado.STATUS_FECHADO,
                     tipo=Chamado.TIPO_DUVIDA)
        for i in range(5):
            novo_chamado(cls.org_b, cls.admin_b, titulo=f'B{i}')

    def setUp(self):
        self.client.force_login(self.admin_a)


class MetricasTests(DashboardBase):
    def test_total_e_status_so_da_organizacao(self):
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['kpis'], {
            'total': 3, 'abertos': 1, 'em_atendimento': 1, 'concluidos': 1, 'atrasados': 0,
        })

    def test_outra_organizacao_ve_os_seus_numeros(self):
        self.client.force_login(self.admin_b)
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.context['kpis']['total'], 5)
        self.assertEqual(sum(m['total'] for m in r.context['por_mes']), 5)

    def test_distribuicoes_somam_o_total(self):
        r = self.client.get(reverse('dashboard'))
        por_tipo = {d['rotulo']: d['total'] for d in r.context['por_tipo']}
        self.assertEqual(por_tipo, {'Incidente': 2, 'Requisição': 0, 'Dúvida': 1})
        self.assertEqual(sum(d['total'] for d in r.context['por_status']), 3)
        self.assertEqual(r.context['ranking_equipes'][0]['total'], 3)

    def test_atrasados(self):
        atrasado = novo_chamado(self.org_a, self.admin_a, titulo='Atrasado')
        Chamado.objects.filter(pk=atrasado.pk).update(data_limite=timezone.now() - timedelta(hours=1))
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.context['kpis']['atrasados'], 1)
        self.assertEqual([c.titulo for c in r.context['atrasados']], ['Atrasado'])

    def test_periodo_filtra(self):
        antigo = Chamado.objects.get(titulo='A1')
        Chamado.objects.filter(pk=antigo.pk).update(data_criacao=timezone.now() - timedelta(days=60))
        hoje = timezone.localdate()
        r = self.client.get(reverse('dashboard'), {'inicio': (hoje - timedelta(days=7)).isoformat()})
        self.assertEqual(r.context['kpis']['total'], 2)
        r = self.client.get(reverse('dashboard'), {'fim': (hoje - timedelta(days=30)).isoformat()})
        self.assertEqual(r.context['kpis']['total'], 1)
        self.assertEqual(len(r.context['por_mes']), 1)

    def test_data_invalida_nao_da_500(self):
        r = self.client.get(reverse('dashboard'), {'inicio': 'abc'})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].errors)
        self.assertEqual(r.context['kpis']['total'], 3)

    def test_inicio_depois_do_fim_e_recusado(self):
        r = self.client.get(reverse('dashboard'), {'inicio': '2026-12-31', 'fim': '2026-01-01'})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].non_field_errors())

    def test_dashboard_vazio_sem_erro(self):
        org = Organizacao.objects.create(nome='Vazia')
        vazio = User.objects.create_user('vazio', password='x')
        Perfil.objects.create(usuario=vazio, organizacao=org, papel=Perfil.PAPEL_ADMIN)
        self.client.force_login(vazio)
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['kpis']['total'], 0)
        self.assertEqual(r.context['por_mes'], [])
        self.assertContains(r, 'Sem dados no período.')


class PapelTests(DashboardBase):
    def test_operador_ve_cartoes_mas_nao_series_nem_atrasados(self):
        self.client.force_login(self.operador_a)
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['kpis']['total'], 3)
        self.assertNotIn('por_mes', r.context)
        self.assertEqual(r.context['atrasados'], [])
        self.assertNotContains(r, 'Exportar CSV')

    def test_operador_nao_exporta_csv(self):
        self.client.force_login(self.operador_a)
        self.assertEqual(self.client.get(reverse('dashboard_csv')).status_code, 403)


class CsvTests(DashboardBase):
    def linhas(self, resposta):
        texto = resposta.content.decode('utf-8-sig')
        return list(csv.reader(io.StringIO(texto), delimiter=';'))

    def test_csv_so_da_organizacao_e_do_periodo(self):
        r = self.client.get(reverse('dashboard_csv'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('attachment', r['Content-Disposition'])
        linhas = self.linhas(r)
        self.assertEqual(linhas[0][0], 'Número')
        self.assertEqual(sorted(l[1] for l in linhas[1:]), ['A1', 'A2', 'A3'])

    def test_csv_neutraliza_formula(self):
        novo_chamado(self.org_a, self.admin_a, titulo='=HYPERLINK("http://x")')
        titulos = [l[1] for l in self.linhas(self.client.get(reverse('dashboard_csv')))[1:]]
        self.assertIn('\'=HYPERLINK("http://x")', titulos)


class DesempenhoTests(DashboardBase):
    def test_metricas_em_numero_fixo_de_consultas(self):
        base = dashboard.base_do_dashboard(self.org_a)
        with self.assertNumQueries(6):
            dashboard.metricas(base)

    def contar(self, url):
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(url)
        return len(ctx)

    def test_tela_e_csv_sem_n_mais_1(self):
        antes = (self.contar(reverse('dashboard')), self.contar(reverse('dashboard_csv')))
        for i in range(10):
            novo_chamado(self.org_a, self.admin_a, titulo=f'extra {i}',
                         data_limite=None, responsavel=self.operador_a)
        Chamado.objects.filter(titulo__startswith='extra').update(
            data_limite=timezone.now() - timedelta(hours=1))
        depois = (self.contar(reverse('dashboard')), self.contar(reverse('dashboard_csv')))
        self.assertEqual(antes, depois)


class DashboardApiTests(DashboardBase):
    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(self.admin_a)

    def test_api_retorna_metricas_da_organizacao(self):
        r = self.api.get(reverse('api-dashboard'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['kpis']['total'], 3)
        self.assertIn('por_mes', r.data)

    def test_api_operador_sem_series(self):
        self.api.force_authenticate(self.operador_a)
        r = self.api.get(reverse('api-dashboard'))
        self.assertNotIn('por_mes', r.data)

    def test_api_data_invalida_da_400(self):
        r = self.api.get(reverse('api-dashboard'), {'inicio': 'abc'})
        self.assertEqual(r.status_code, 400)

    def test_api_exige_login(self):
        self.assertIn(APIClient().get(reverse('api-dashboard')).status_code, (401, 403))
