from django.urls import path
from . import views

urlpatterns = [
    path('', views.painel, name='painel'),
    path('cadastro/', views.cadastro, name='cadastro'),

    #chamados
    path('chamados/novo/', views.ChamadoCreateView.as_view(), name='chamado_novo'),
    path('chamados/<int:pk>/', views.ChamadoDetailView.as_view(), name='chamado_detalhe'),
    path('chamados/<int:pk>/editar/', views.ChamadoUpdateView.as_view(), name='chamado_editar'),
    path('chamados/<int:pk>/excluir/', views.ChamadoDeleteView.as_view(), name='chamado_excluir'),

    #equipes
    path('equipes/', views.EquipeListView.as_view(), name='equipe_lista'),
    path('equipes/novo/', views.EquipeCreateView.as_view(), name='equipe_novo'),
    path('equipes/<int:pk>/editar/', views.EquipeUpdateView.as_view(), name='equipe_editar'),
    path('equipes/<int:pk>/excluir/', views.EquipeDeleteView.as_view(), name='equipe_excluir'),

    #categorias
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_lista'),
    path('categorias/novo/', views.CategoriaCreateView.as_view(), name='categoria_novo'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/excluir/', views.CategoriaDeleteView.as_view(), name='categoria_excluir'),

    #prioridades
    path('prioridades/', views.PrioridadeListView.as_view(), name='prioridade_lista'),
    path('prioridades/novo/', views.PrioridadeCreateView.as_view(), name='prioridade_novo'),
    path('prioridades/<int:pk>/editar/', views.PrioridadeUpdateView.as_view(), name='prioridade_editar'),
    path('prioridades/<int:pk>/excluir/', views.PrioridadeDeleteView.as_view(), name='prioridade_excluir'),

    #SLAs
    path('slas/', views.SLAListView.as_view(), name='sla_lista'),
    path('slas/novo/', views.SLACreateView.as_view(), name='sla_novo'),
    path('slas/<int:pk>/editar/', views.SLAUpdateView.as_view(), name='sla_editar'),
    path('slas/<int:pk>/excluir/', views.SLADeleteView.as_view(), name='sla_excluir'),
]
