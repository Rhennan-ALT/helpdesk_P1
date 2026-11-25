from functools import wraps

from django.core.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Perfil

MENSAGEM = 'Você não tem permissão para acessar esta página.'


def tem_papel(user, papel):
    perfil = getattr(user, 'perfil', None)
    return perfil is not None and perfil.papel == papel


def eh_admin(user):
    return tem_papel(user, Perfil.PAPEL_ADMIN)


def papel_requerido(papel):
    def decorator(view):
        @wraps(view)
        def _view(request, *args, **kwargs):
            if not tem_papel(request.user, papel):
                raise PermissionDenied(MENSAGEM)
            return view(request, *args, **kwargs)
        return _view
    return decorator


class PapelRequeridoMixin:
    papel_requerido = Perfil.PAPEL_ADMIN

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not tem_papel(request.user, self.papel_requerido):
            raise PermissionDenied(MENSAGEM)
        return super().dispatch(request, *args, **kwargs)


class AdminOuSomenteLeitura(BasePermission):
    message = 'Apenas administradores podem alterar este cadastro.'

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or eh_admin(request.user)


class ExcluirSomenteAdmin(BasePermission):
    message = 'Apenas administradores podem excluir chamados.'

    def has_permission(self, request, view):
        return request.method != 'DELETE' or eh_admin(request.user)
