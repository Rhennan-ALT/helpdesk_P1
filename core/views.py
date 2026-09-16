from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CadastroUsuarioForm, CategoriaForm, ChamadoForm, EquipeForm, PrioridadeForm, SLAForm
from .models import SLA, Categoria, Chamado, Equipe, Prioridade


#autenticar
def cadastro(request):

    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, 'Cadastro realizado com sucesso.')
            return redirect('painel')

    else:
        form = CadastroUsuarioForm()
    return render(request, 'core/cadastro.html', {'form': form})


#painel
@login_required
def painel(request):

    chamados = Chamado.objects.select_related('equipe', 'categoria', 'prioridade', 'responsavel')

    if not request.user.is_staff:
        chamados = chamados.filter(Q(solicitante=request.user) | Q(responsavel=request.user))

    status_selecionado = request.GET.get('status', '')
    if status_selecionado:
        chamados = chamados.filter(status=status_selecionado)

    apenas_atrasados = request.GET.get('atrasados') == '1'
    if apenas_atrasados:
        chamados = [c for c in chamados if c.esta_atrasado]

    contexto = {
        'chamados': chamados,
        'status_choices': Chamado.STATUS_CHOICES,
        'status_selecionado': status_selecionado,
        'apenas_atrasados': apenas_atrasados,
    }
    return render(request, 'core/painel.html', contexto)


#crud do chamado
class ChamadoPermissaoMixin(UserPassesTestMixin):

    def test_func(self):
        chamado = self.get_object()
        return chamado.usuario_pode_gerenciar(self.request.user)

class ChamadoCreateView(LoginRequiredMixin, CreateView):
    model = Chamado
    form_class = ChamadoForm
    template_name = 'core/chamado_form.html'
    success_url = reverse_lazy('painel')

    def form_valid(self, form):
        form.instance.solicitante = self.request.user
        messages.success(self.request, 'Chamado aberto.')
        return super().form_valid(form)

class ChamadoDetailView(LoginRequiredMixin, ChamadoPermissaoMixin, DetailView):
    model = Chamado
    template_name = 'core/chamado_detail.html'
    context_object_name = 'chamado'

class ChamadoUpdateView(LoginRequiredMixin, ChamadoPermissaoMixin, UpdateView):
    model = Chamado
    form_class = ChamadoForm
    template_name = 'core/chamado_form.html'
    success_url = reverse_lazy('painel')

    def form_valid(self, form):
        messages.success(self.request, 'Chamado atualizado.')
        return super().form_valid(form)

class ChamadoDeleteView(LoginRequiredMixin, ChamadoPermissaoMixin, DeleteView):
    model = Chamado
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('painel')

    def form_valid(self, form):
        messages.success(self.request, 'Chamado excluído.')
        return super().form_valid(form)


#crud da equipe
class EquipeListView(LoginRequiredMixin, ListView):
    model = Equipe
    template_name = 'core/equipe_list.html'
    context_object_name = 'equipes'

class EquipeCreateView(LoginRequiredMixin, CreateView):
    model = Equipe
    form_class = EquipeForm
    template_name = 'core/equipe_form.html'
    success_url = reverse_lazy('equipe_lista')

class EquipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipe
    form_class = EquipeForm
    template_name = 'core/equipe_form.html'
    success_url = reverse_lazy('equipe_lista')

class EquipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Equipe
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('equipe_lista')


#crud das categorias
class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'core/categoria_list.html'
    context_object_name = 'categorias'

class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'core/categoria_form.html'
    success_url = reverse_lazy('categoria_lista')

class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'core/categoria_form.html'
    success_url = reverse_lazy('categoria_lista')

class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('categoria_lista')


# crud das prioridadas
class PrioridadeListView(LoginRequiredMixin, ListView):
    model = Prioridade
    template_name = 'core/prioridade_list.html'
    context_object_name = 'prioridades'

class PrioridadeCreateView(LoginRequiredMixin, CreateView):
    model = Prioridade
    form_class = PrioridadeForm
    template_name = 'core/prioridade_form.html'
    success_url = reverse_lazy('prioridade_lista')

class PrioridadeUpdateView(LoginRequiredMixin, UpdateView):
    model = Prioridade
    form_class = PrioridadeForm
    template_name = 'core/prioridade_form.html'
    success_url = reverse_lazy('prioridade_lista')

class PrioridadeDeleteView(LoginRequiredMixin, DeleteView):
    model = Prioridade
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('prioridade_lista')


#crud do SLA
class SLAListView(LoginRequiredMixin, ListView):
    model = SLA
    template_name = 'core/sla_list.html'
    context_object_name = 'slas'

class SLACreateView(LoginRequiredMixin, CreateView):
    model = SLA
    form_class = SLAForm
    template_name = 'core/sla_form.html'
    success_url = reverse_lazy('sla_lista')

class SLAUpdateView(LoginRequiredMixin, UpdateView):
    model = SLA
    form_class = SLAForm
    template_name = 'core/sla_form.html'
    success_url = reverse_lazy('sla_lista')

class SLADeleteView(LoginRequiredMixin, DeleteView):
    model = SLA
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('sla_lista')