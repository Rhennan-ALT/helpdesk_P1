from django.urls import path

from . import api_views

urlpatterns = [
    path('chamados/', api_views.ChamadoListCreateAPIView.as_view(), name='api-chamado-list'),
    path('chamados/<int:pk>/', api_views.ChamadoRetrieveUpdateDestroyAPIView.as_view(), name='api-chamado-detail'),

    path('equipes/', api_views.EquipeListCreateAPIView.as_view(), name='api-equipe-list'),
    path('equipes/<int:pk>/', api_views.EquipeRetrieveUpdateDestroyAPIView.as_view(), name='api-equipe-detail'),

    path('categorias/', api_views.CategoriaListCreateAPIView.as_view(), name='api-categoria-list'),
    path('categorias/<int:pk>/', api_views.CategoriaRetrieveUpdateDestroyAPIView.as_view(), name='api-categoria-detail'),

    path('prioridades/', api_views.PrioridadeListCreateAPIView.as_view(), name='api-prioridade-list'),
    path('prioridades/<int:pk>/', api_views.PrioridadeRetrieveUpdateDestroyAPIView.as_view(), name='api-prioridade-detail'),

    path('slas/', api_views.SLAListCreateAPIView.as_view(), name='api-sla-list'),
    path('slas/<int:pk>/', api_views.SLARetrieveUpdateDestroyAPIView.as_view(), name='api-sla-detail'),
]
