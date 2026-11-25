import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import ProtectedError, Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CadastroUsuarioForm, CategoriaForm, ChamadoForm, EquipeForm, PrioridadeForm, SLAForm
from . import dashboard as metricas_dashboard
from .dados_iniciais import criar_dados_iniciais
from .models import SLA, Categoria, Chamado, Equipe, Organizacao, Perfil, Prioridade
from .organizacao import org_atual
from .permissoes import PapelRequeridoMixin, eh_admin, papel_requerido


class DaOrganizacaoMixin(LoginRequiredMixin):

    def get_queryset(self):
        return super().get_queryset().filter(organizacao=org_atual(self.request))


class FormDaOrganizacaoMixin(DaOrganizacaoMixin):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['org'] = org_atual(self.request)
        return kwargs

    def form_valid(self, form):
        form.instance.organizacao = org_atual(self.request)
        return super().form_valid(form)


class ExclusaoProtegidaMixin:

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, 'Não é possível excluir: há chamados vinculados a este registro.')
            return redirect(self.success_url)


#autenticar
def cadastro(request):

    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                usuario = form.save()
                org = Organizacao.objects.create(nome=form.cleaned_data['organizacao'])
                Perfil.objects.create(usuario=usuario, organizacao=org, papel=Perfil.PAPEL_ADMIN)
                criar_dados_iniciais(org)
            login(request, usuario)
            messages.success(request, 'Cadastro realizado com sucesso.')
            return redirect('painel')

    else:
        form = CadastroUsuarioForm()
    return render(request, 'core/cadastro.html', {'form': form})


#painel
@login_required
def painel(request):

    chamados = Chamado.objects.filter(organizacao=org_atual(request)).select_related(
        'equipe', 'categoria', 'prioridade', 'responsavel',
    )

    if not eh_admin(request.user):
        chamados = chamados.filter(Q(solicitante=request.user) | Q(responsavel=request.user))

    status_selecionado = request.GET.get('status', '')
    if status_selecionado:
        chamados = chamados.filter(status=status_selecionado)

    apenas_atrasados = request.GET.get('atrasados') == '1'
    if apenas_atrasados:
        chamados = chamados.atrasados()

    tipo_selecionado = request.GET.get('tipo', '')
    if tipo_selecionado:
        chamados = chamados.filter(tipo=tipo_selecionado)
    
    busca = request.GET.get('q', '').strip()
    if busca:
        chamados = chamados.filter(Q(titulo__icontains=busca) | Q(descricao__icontains=busca))

    contexto = {
        'chamados': chamados,
        'status_choices': Chamado.STATUS_CHOICES,
        'status_selecionado': status_selecionado,
        'apenas_atrasados': apenas_atrasados,
        'tipo_choices': Chamado.TIPO_CHOICES,
        'tipo_selecionado': tipo_selecionado,
        'busca': busca,
    }
    return render(request, 'core/painel.html', contexto)


#crud do chamado
class ChamadoPermissaoMixin(UserPassesTestMixin):

    def test_func(self):
        chamado = self.get_object()
        return chamado.usuario_pode_gerenciar(self.request.user)

class ChamadoCreateView(FormDaOrganizacaoMixin, CreateView):
    model = Chamado
    form_class = ChamadoForm
    template_name = 'core/chamado_form.html'
    success_url = reverse_lazy('painel')

    def form_valid(self, form):
        form.instance.solicitante = self.request.user
        messages.success(self.request, 'Chamado aberto.')
        return super().form_valid(form)

class ChamadoDetailView(DaOrganizacaoMixin, ChamadoPermissaoMixin, DetailView):
    model = Chamado
    template_name = 'core/chamado_detail.html'
    context_object_name = 'chamado'

class ChamadoUpdateView(FormDaOrganizacaoMixin, ChamadoPermissaoMixin, UpdateView):
    model = Chamado
    form_class = ChamadoForm
    template_name = 'core/chamado_form.html'
    success_url = reverse_lazy('painel')

    def form_valid(self, form):
        messages.success(self.request, 'Chamado atualizado.')
        return super().form_valid(form)

class ChamadoDeleteView(DaOrganizacaoMixin, PapelRequeridoMixin, ChamadoPermissaoMixin, DeleteView):
    model = Chamado
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('painel')

    def form_valid(self, form):
        messages.success(self.request, 'Chamado excluído.')
        return super().form_valid(form)


#crud da equipe
class EquipeListView(DaOrganizacaoMixin, PapelRequeridoMixin, ListView):
    model = Equipe
    template_name = 'core/equipe_list.html'
    context_object_name = 'equipes'

class EquipeCreateView(FormDaOrganizacaoMixin, PapelRequeridoMixin, CreateView):
    model = Equipe
    form_class = EquipeForm
    template_name = 'core/equipe_form.html'
    success_url = reverse_lazy('equipe_lista')

class EquipeUpdateView(FormDaOrganizacaoMixin, PapelRequeridoMixin, UpdateView):
    model = Equipe
    form_class = EquipeForm
    template_name = 'core/equipe_form.html'
    success_url = reverse_lazy('equipe_lista')

class EquipeDeleteView(DaOrganizacaoMixin, PapelRequeridoMixin, ExclusaoProtegidaMixin, DeleteView):
    model = Equipe
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('equipe_lista')


#crud das categorias
class CategoriaListView(DaOrganizacaoMixin, PapelRequeridoMixin, ListView):
    model = Categoria
    template_name = 'core/categoria_list.html'
    context_object_name = 'categorias'

class CategoriaCreateView(FormDaOrganizacaoMixin, PapelRequeridoMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'core/categoria_form.html'
    success_url = reverse_lazy('categoria_lista')

class CategoriaUpdateView(FormDaOrganizacaoMixin, PapelRequeridoMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'core/categoria_form.html'
    success_url = reverse_lazy('categoria_lista')

class CategoriaDeleteView(DaOrganizacaoMixin, PapelRequeridoMixin, ExclusaoProtegidaMixin, DeleteView):
    model = Categoria
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('categoria_lista')


# crud das prioridadas
class PrioridadeListView(DaOrganizacaoMixin, PapelRequeridoMixin, ListView):
    model = Prioridade
    template_name = 'core/prioridade_list.html'
    context_object_name = 'prioridades'

class PrioridadeCreateView(FormDaOrganizacaoMixin, PapelRequeridoMixin, CreateView):
    model = Prioridade
    form_class = PrioridadeForm
    template_name = 'core/prioridade_form.html'
    success_url = reverse_lazy('prioridade_lista')

class PrioridadeUpdateView(FormDaOrganizacaoMixin, PapelRequeridoMixin, UpdateView):
    model = Prioridade
    form_class = PrioridadeForm
    template_name = 'core/prioridade_form.html'
    success_url = reverse_lazy('prioridade_lista')

class PrioridadeDeleteView(DaOrganizacaoMixin, PapelRequeridoMixin, ExclusaoProtegidaMixin, DeleteView):
    model = Prioridade
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('prioridade_lista')


#crud do SLA
class SLAListView(DaOrganizacaoMixin, PapelRequeridoMixin, ListView):
    model = SLA
    template_name = 'core/sla_list.html'
    context_object_name = 'slas'

class SLACreateView(FormDaOrganizacaoMixin, PapelRequeridoMixin, CreateView):
    model = SLA
    form_class = SLAForm
    template_name = 'core/sla_form.html'
    success_url = reverse_lazy('sla_lista')

class SLAUpdateView(FormDaOrganizacaoMixin, PapelRequeridoMixin, UpdateView):
    model = SLA
    form_class = SLAForm
    template_name = 'core/sla_form.html'
    success_url = reverse_lazy('sla_lista')

class SLADeleteView(DaOrganizacaoMixin, PapelRequeridoMixin, DeleteView):
    model = SLA
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('sla_lista')


#dashboard
@login_required
def dashboard(request):
    base, form = metricas_dashboard.filtrar_periodo(
        request, metricas_dashboard.base_do_dashboard(org_atual(request)),
    )
    admin = eh_admin(request.user)
    contexto = metricas_dashboard.metricas(base, com_series=admin)
    contexto.update({
        'form': form,
        'eh_admin': admin,
        'atrasados': metricas_dashboard.atrasados(base) if admin else [],
    })
    return render(request, 'core/dashboard.html', contexto)


def _celula_segura(valor):
    texto = '' if valor is None else str(valor)
    if texto[:1] in ('=', '+', '-', '@'):
        return "'" + texto
    return texto


@login_required
@papel_requerido(Perfil.PAPEL_ADMIN)
def exportar_csv(request):
    base, _ = metricas_dashboard.filtrar_periodo(
        request, metricas_dashboard.base_do_dashboard(org_atual(request)),
    )
    chamados = base.select_related('equipe', 'categoria', 'prioridade', 'solicitante', 'responsavel')

    resposta = HttpResponse(content_type='text/csv; charset=utf-8')
    resposta['Content-Disposition'] = 'attachment; filename="chamados.csv"'
    resposta.write('\ufeff')
    escritor = csv.writer(resposta, delimiter=';')
    escritor.writerow([
        'Número', 'Título', 'Tipo', 'Status', 'Equipe', 'Categoria', 'Prioridade',
        'Solicitante', 'Responsável', 'Aberto em', 'Prazo (SLA)', 'Fechado em', 'Atrasado',
    ])
    formato = '%d/%m/%Y %H:%M'
    for c in chamados:
        escritor.writerow([_celula_segura(v) for v in (
            c.pk, c.titulo, c.get_tipo_display(), c.get_status_display(),
            c.equipe.nome, c.categoria.nome, c.prioridade.nome,
            c.solicitante.username, c.responsavel.username if c.responsavel else '',
            timezone.localtime(c.data_criacao).strftime(formato),
            timezone.localtime(c.data_limite).strftime(formato) if c.data_limite else '',
            timezone.localtime(c.data_fechamento).strftime(formato) if c.data_fechamento else '',
            'Sim' if c.esta_atrasado else 'Não',
        )])
    return resposta

