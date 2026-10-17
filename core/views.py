from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from comunidades.models import Comunidad
from eventos.models import Evento, Inscripcion
from eventos.queries import eventos_con_cupos


def inicio(request):
    ahora = timezone.now()
    proximos = eventos_con_cupos(request.user).filter(inicio__gte=ahora)[:4]
    emergentes = Comunidad.objects.filter(estado=Comunidad.Estado.ACTIVA, tipo=Comunidad.Tipo.EMERGENTE)

    # Confirmación dinámica (P-13): eventos en las próximas 48 h sin respuesta.
    por_confirmar = None
    if request.user.is_authenticated:
        por_confirmar = (Inscripcion.objects
                         .filter(usuario=request.user, estado=Inscripcion.Estado.CONFIRMADA,
                                 confirmo_asistencia__isnull=True, evento__pedir_confirmacion=True,
                                 evento__inicio__gte=ahora, evento__inicio__lte=ahora + timedelta(hours=48))
                         .select_related('evento').order_by('evento__inicio').first())

    afiches = list(eventos_con_cupos(request.user).filter(inicio__gte=ahora).order_by('?')[:3])
    return render(request, 'core/inicio.html', {
        'proximos': proximos, 'emergentes': emergentes, 'por_confirmar': por_confirmar, 'afiches': afiches,
    })


def ingresar(request):
    """Simula el ingreso con OAuth U. de Chile (P-12). En producción: django-allauth u OIDC."""
    if request.method == 'POST':
        user = get_user_model().objects.filter(username='valentina').first()
        if not user:
            messages.error(request, 'Faltan los datos de prueba. Ejecuta: python manage.py cargar_demo')
            return redirect('core:login')
        login(request, user)
        messages.success(request, f'Ingresaste como {user.get_full_name()}')
        return redirect(request.POST.get('next') or 'core:inicio')
    return render(request, 'cuentas/login.html', {'next': request.GET.get('next', '')})


@require_POST
def salir(request):
    logout(request)
    messages.success(request, 'Cerraste sesión')
    return redirect('core:inicio')


@require_POST
def demo_como(request):
    """Barra morada de la demo: cambia de perfil sin contraseña. Solo con DEMO_MODE."""
    if not getattr(settings, 'DEMO_MODE', False):
        raise Http404
    from .context_processors import DEMO_USUARIOS
    usuarios = {rol: username for rol, _, username in DEMO_USUARIOS}
    username = usuarios.get(request.POST.get('rol'))
    if username is None:
        logout(request)
        messages.success(request, 'Viendo como visitante sin sesión')
    else:
        user = get_user_model().objects.filter(username=username).first()
        if not user:
            messages.error(request, 'Faltan los datos de prueba. Ejecuta: python manage.py cargar_demo')
        else:
            login(request, user)
            messages.success(request, f'Viendo como {user.get_full_name()}')
    destino = request.POST.get('volver') or '/'
    return redirect(destino if destino.startswith('/') and not destino.startswith('//') else '/')


def mapa_django(request):
    return render(request, 'core/mapa_django.html')
