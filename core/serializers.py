from rest_framework import serializers
from .models import SLA, Categoria, Chamado, Equipe, Prioridade


class EquipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipe
        fields = ['id', 'nome']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome']


class PrioridadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prioridade
        fields = ['id', 'nome', 'ordem']


class SLASerializer(serializers.ModelSerializer):
    class Meta:
        model = SLA
        fields = ['id', 'categoria', 'prioridade', 'horas']


class ChamadoSerializer(serializers.ModelSerializer):
    esta_atrasado = serializers.BooleanField(read_only=True)

    class Meta:
        model = Chamado
        fields = [
            'id', 'titulo', 'descricao', 'status',
            'solicitante', 'responsavel', 'equipe', 'categoria', 'prioridade',
            'data_criacao', 'data_limite', 'data_fechamento', 'esta_atrasado',
        ]

        read_only_fields = [
            'solicitante', 'data_criacao', 'data_limite', 'data_fechamento',
        ]
