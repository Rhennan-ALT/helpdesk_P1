from django.contrib import admin
from .models import Categoria, Chamado, Equipe, Prioridade, SLA


@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Prioridade)
class PrioridadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem')
    ordering = ('ordem',)

@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'prioridade', 'horas')
    list_filter = ('categoria', 'prioridade')

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'titulo', 'status', 'equipe', 'categoria', 'prioridade',
        'solicitante', 'responsavel', 'data_criacao', 'data_limite', 'esta_atrasado',
    )
    list_filter = ('status', 'equipe', 'categoria', 'prioridade')
    search_fields = ('titulo', 'descricao')
    readonly_fields = ('data_criacao', 'data_limite', 'data_fechamento')

    @admin.display(boolean=True, description='Atrasado?')
    def esta_atrasado(self, obj):
        return obj.esta_atrasado

