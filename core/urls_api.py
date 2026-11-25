from django.urls import path

from . import views_api

urlpatterns = [
    path('dashboard/', views_api.DashboardAPIView.as_view(), name='api-dashboard'),

    path('chamados/', views_api.ChamadoListCreateAPIView.as_view(), name='api-chamado-list'),
    path('chamados/<int:pk>/', views_api.ChamadoRetrieveUpdateDestroyAPIView.as_view(), name='api-chamado-detail'),

    path('equipes/', views_api.EquipeListCreateAPIView.as_view(), name='api-equipe-list'),
    path('equipes/<int:pk>/', views_api.EquipeRetrieveUpdateDestroyAPIView.as_view(), name='api-equipe-detail'),

    path('categorias/', views_api.CategoriaListCreateAPIView.as_view(), name='api-categoria-list'),
    path('categorias/<int:pk>/', views_api.CategoriaRetrieveUpdateDestroyAPIView.as_view(), name='api-categoria-detail'),

    path('prioridades/', views_api.PrioridadeListCreateAPIView.as_view(), name='api-prioridade-list'),
    path('prioridades/<int:pk>/', views_api.PrioridadeRetrieveUpdateDestroyAPIView.as_view(), name='api-prioridade-detail'),

    path('slas/', views_api.SLAListCreateAPIView.as_view(), name='api-sla-list'),
    path('slas/<int:pk>/', views_api.SLARetrieveUpdateDestroyAPIView.as_view(), name='api-sla-detail'),
]
