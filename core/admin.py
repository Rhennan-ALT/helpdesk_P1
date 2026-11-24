from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import SLA, Categoria, Chamado, Equipe, Organizacao, Perfil, Prioridade


@admin.register(Organizacao)
class OrganizacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criada_em')
    search_fields = ('nome',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'organizacao')
    list_filter = ('organizacao',)
    search_fields = ('usuario__username',)

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False

admin.site.unregister(User)

@admin.register(User)
class UsuarioAdmin(UserAdmin):
    inlines = [PerfilInline]
    list_display = ('username', 'email', 'organizacao', 'is_staff')
    list_filter = ('perfil__organizacao', 'is_staff', 'is_superuser')

    @admin.display(description='Organização')
    def organizacao(self, obj):
        perfil = getattr(obj, 'perfil', None)
        return perfil.organizacao if perfil else '-'

@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'organizacao')
    list_filter = ('organizacao',)
    search_fields = ('nome',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'organizacao')
    list_filter = ('organizacao',)
    search_fields = ('nome',)

@admin.register(Prioridade)
class PrioridadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem', 'organizacao')
    list_filter = ('organizacao',)
    ordering = ('organizacao', 'ordem')

@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'prioridade', 'horas', 'organizacao')
    list_filter = ('organizacao', 'categoria', 'prioridade')

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'titulo', 'status', 'equipe', 'categoria', 'prioridade',
        'solicitante', 'responsavel', 'data_criacao', 'data_limite', 'esta_atrasado', 'tipo',
        'organizacao',
    )
    list_filter = ('organizacao', 'status', 'equipe', 'categoria', 'prioridade', 'tipo')
    search_fields = ('titulo', 'descricao')
    readonly_fields = ('data_criacao', 'data_limite', 'data_fechamento')

    @admin.display(boolean=True, description='Atrasado?')
    def esta_atrasado(self, obj):
        return obj.esta_atrasado
