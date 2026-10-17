"""Perfiles de la Tarea 2: Visitante (P-08), Estudiante (P-05), Coordinador (P-06), Administrador (P-07)."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from comunidades.models import Comunidad, Membresia


def rol_de(user):
    if not user.is_authenticated:
        return 'visitante'
    if user.is_staff:
        return 'admin'
    if Membresia.objects.filter(usuario=user, rol=Membresia.Rol.COORDINADOR).exists():
        return 'coordinador'
    return 'estudiante'


def comunidades_coordinadas(user):
    if not user.is_authenticated:
        return Comunidad.objects.none()
    return Comunidad.objects.filter(membresias__usuario=user, membresias__rol=Membresia.Rol.COORDINADOR)


def staff_requerido(vista):
    @wraps(vista)
    @login_required
    def envoltura(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return vista(request, *args, **kwargs)
    return envoltura
