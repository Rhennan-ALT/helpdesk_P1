from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .forms import PeriodoForm
from .models import Chamado


def base_do_dashboard(org):
    return Chamado.objects.filter(organizacao=org)


def filtrar_periodo(request, qs):
    form = PeriodoForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['inicio']:
            qs = qs.filter(data_criacao__date__gte=form.cleaned_data['inicio'])
        if form.cleaned_data['fim']:
            qs = qs.filter(data_criacao__date__lte=form.cleaned_data['fim'])
    return qs, form


def kpis(base):
    return base.aggregate(
        total=Count('id'),
        abertos=Count('id', filter=Q(status=Chamado.STATUS_ABERTO)),
        em_atendimento=Count('id', filter=Q(status=Chamado.STATUS_ANDAMENTO)),
        concluidos=Count('id', filter=Q(status=Chamado.STATUS_FECHADO)),
        atrasados=Count('id', filter=Q(data_limite__lt=timezone.now()) & ~Q(status=Chamado.STATUS_FECHADO)),
    )


def ranking_equipes(base, limite=5):
    return list(
        base.values('equipe__nome')
        .annotate(total=Count('id'))
        .order_by('-total', 'equipe__nome')[:limite]
    )


def ranking_categorias(base, limite=5):
    return list(
        base.values('categoria__nome')
        .annotate(total=Count('id'))
        .order_by('-total', 'categoria__nome')[:limite]
    )


def _distribuicao(base, campo, choices):
    contagem = dict(base.values_list(campo).annotate(total=Count('id')).order_by())
    return [{'rotulo': rotulo, 'total': contagem.get(valor, 0)} for valor, rotulo in choices]


def por_status(base):
    return _distribuicao(base, 'status', Chamado.STATUS_CHOICES)


def por_tipo(base):
    return _distribuicao(base, 'tipo', Chamado.TIPO_CHOICES)


def por_mes(base):
    linhas = (
        base.annotate(mes=TruncMonth('data_criacao'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    return [{'mes': linha['mes'].strftime('%m/%Y'), 'total': linha['total']} for linha in linhas]


def atrasados(base, limite=10):
    return list(
        base.atrasados()
        .select_related('equipe', 'prioridade')
        .order_by('data_limite')[:limite]
    )


def metricas(base, com_series=True):
    dados = {
        'kpis': kpis(base),
        'ranking_equipes': ranking_equipes(base),
        'ranking_categorias': ranking_categorias(base),
        'por_status': por_status(base),
        'por_tipo': por_tipo(base),
    }
    if com_series:
        dados['por_mes'] = por_mes(base)
    return dados
