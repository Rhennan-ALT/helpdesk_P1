from django.db.models import ProtectedError, Q
from rest_framework import generics
from rest_framework.exceptions import APIException

from .models import SLA, Categoria, Chamado, Equipe, Prioridade
from .serializers import (
    CategoriaSerializer, ChamadoSerializer, EquipeSerializer,
    PrioridadeSerializer, SLASerializer,
)

class ConflitoProtegido(APIException):
    status_code = 409
    default_detail = 'Não é possível excluir: há chamados vinculados a este registro.'
    default_code = 'protegido'


class _ExclusaoProtegidaMixin:
    """Equipe/Categoria/Prioridade usam on_delete=PROTECT em Chamado: devolve 409 em vez de 500."""

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ConflitoProtegido()


class _ChamadoQuerysetMixin:
    """Mesma regra do painel/site: usuário comum só acessa chamados em que é
    solicitante ou responsável; staff acessa todos. Fora disso, 404."""

    def get_queryset(self):
        qs = Chamado.objects.select_related(
            'solicitante', 'responsavel', 'equipe', 'categoria', 'prioridade',
        )
        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(Q(solicitante=user) | Q(responsavel=user))
        return qs


class ChamadoListCreateAPIView(_ChamadoQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = ChamadoSerializer

    def perform_create(self, serializer):
        serializer.save(solicitante=self.request.user)


class ChamadoRetrieveUpdateDestroyAPIView(_ChamadoQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChamadoSerializer


class EquipeListCreateAPIView(generics.ListCreateAPIView):
    queryset = Equipe.objects.all()
    serializer_class = EquipeSerializer


class EquipeRetrieveUpdateDestroyAPIView(_ExclusaoProtegidaMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Equipe.objects.all()
    serializer_class = EquipeSerializer


class CategoriaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class CategoriaRetrieveUpdateDestroyAPIView(_ExclusaoProtegidaMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class PrioridadeListCreateAPIView(generics.ListCreateAPIView):
    queryset = Prioridade.objects.all()
    serializer_class = PrioridadeSerializer


class PrioridadeRetrieveUpdateDestroyAPIView(_ExclusaoProtegidaMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Prioridade.objects.all()
    serializer_class = PrioridadeSerializer


class SLAListCreateAPIView(generics.ListCreateAPIView):
    queryset = SLA.objects.select_related('categoria', 'prioridade')
    serializer_class = SLASerializer


class SLARetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SLA.objects.select_related('categoria', 'prioridade')
    serializer_class = SLASerializer
