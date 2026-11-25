from django.core.exceptions import PermissionDenied

def org_atual(request):
    perfil = getattr(request.user, 'perfil', None)
    if perfil is None:
        raise PermissionDenied(
            'Usuário sem organização vinculada. Peça a um administrador para criar o seu Perfil.'
        )
    return perfil.organizacao
