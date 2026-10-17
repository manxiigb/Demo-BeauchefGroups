from django.conf import settings

from moderacion.models import Reporte
from comunidades.models import Comunidad

from .roles import comunidades_coordinadas, rol_de

DEMO_USUARIOS = [
    ('visitante', 'Visitante', None),
    ('estudiante', 'Estudiante', 'valentina'),
    ('coordinador', 'Coordinador', 'matias'),
    ('admin', 'Administrador', 'paula'),
]


def navegacion(request):
    user = request.user
    rol = rol_de(user)
    ctx = {
        'rol': rol,
        'demo_mode': getattr(settings, 'DEMO_MODE', False),
        'demo_roles': DEMO_USUARIOS,
        'mi_comunidad': comunidades_coordinadas(user).first() if rol == 'coordinador' else None,
        'notif_sin_leer': user.notificaciones.filter(leida=False).count() if user.is_authenticated else 0,
        'pendientes_moderacion': 0,
    }
    ctx['nav_actual'] = _nav_actual(request, ctx['mi_comunidad'])
    if rol == 'admin':
        ctx['pendientes_moderacion'] = (Reporte.objects.filter(estado=Reporte.Estado.PENDIENTE).count()
                                        + Comunidad.objects.filter(estado=Comunidad.Estado.PENDIENTE).count())
    return ctx


def _nav_actual(request, mi_comunidad):
    """Qué ítem del menú marcar como actual."""
    m = request.resolver_match
    if not m:
        return ''
    ns, nombre = m.namespace, m.url_name
    if ns == 'comunidades':
        if nombre == 'nueva':
            return 'registrar'
        if mi_comunidad and m.kwargs.get('slug') == mi_comunidad.slug:
            return 'mi_comunidad'
        return 'comunidades'
    if ns == 'eventos':
        return {'mis_inscripciones': 'mis', 'nuevo': 'publicar'}.get(nombre, 'eventos')
    if ns == 'notificaciones':
        return 'notificaciones'
    if ns == 'moderacion':
        return 'moderacion'
    if ns == 'core':
        return nombre
    return ''
