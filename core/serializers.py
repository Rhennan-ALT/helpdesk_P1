from django.contrib.auth.models import User
from rest_framework import serializers

from .models import SLA, Categoria, Chamado, Equipe, Prioridade
from .organizacao import org_atual


class _DaOrganizacaoSerializerMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request is None:
            return
        org = org_atual(request)
        for campo in self.fields.values():
            if not isinstance(campo, serializers.PrimaryKeyRelatedField) or campo.read_only:
                continue
            if campo.queryset.model is User:
                campo.queryset = campo.queryset.filter(perfil__organizacao=org)
            else:
                campo.queryset = campo.queryset.filter(organizacao=org)


class _NomeUnicoPorOrgSerializerMixin:

    def validate_nome(self, value):
        org = org_atual(self.context['request'])
        repetidos = self.Meta.model.objects.filter(organizacao=org, nome=value)
        if self.instance is not None:
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise serializers.ValidationError('Já existe um registro com este nome na sua organização.')
        return value


class EquipeSerializer(_NomeUnicoPorOrgSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Equipe
        fields = ['id', 'nome']


class CategoriaSerializer(_NomeUnicoPorOrgSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome']


class PrioridadeSerializer(_NomeUnicoPorOrgSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Prioridade
        fields = ['id', 'nome', 'ordem']


class SLASerializer(_DaOrganizacaoSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SLA
        fields = ['id', 'categoria', 'prioridade', 'horas']


class ChamadoSerializer(_DaOrganizacaoSerializerMixin, serializers.ModelSerializer):
    esta_atrasado = serializers.BooleanField(read_only=True)

    class Meta:
        model = Chamado
        fields = [
            'id', 'titulo', 'descricao', 'tipo', 'status',
            'solicitante', 'responsavel', 'equipe', 'categoria', 'prioridade',
            'data_criacao', 'data_limite', 'data_fechamento', 'esta_atrasado',
        ]
        
        read_only_fields = [
            'solicitante', 'data_criacao', 'data_limite', 'data_fechamento',
        ]
