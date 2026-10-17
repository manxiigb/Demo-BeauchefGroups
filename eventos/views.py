from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.roles import comunidades_coordinadas
from moderacion.models import Reporte
from notificaciones.models import Notificacion
from notificaciones.services import notificar

from . import services
from .forms import EventoForm, MensajeForm
from .models import Evento, Inscripcion
from .queries import eventos_con_cupos

FILTROS = [('semana', 'Próximos 10 días'), ('todos', 'Todos'), ('cupos', 'Con cupos'), ('remoto', 'Remotos o híbridos')]


def lista(request):
    """Feed de eventos (P-15)."""
    f = request.GET.get('f', 'semana')
    ahora = timezone.now()
    qs = eventos_con_cupos(request.user).filter(inicio__gte=ahora)
    if f == 'semana':
        qs = qs.filter(inicio__lte=ahora + timedelta(days=10))
    elif f == 'remoto':
        qs = qs.exclude(modalidad=Evento.Modalidad.PRESENCIAL)
    eventos = [e for e in qs if e.libres > 0] if f == 'cupos' else qs
    return render(request, 'eventos/lista.html', {'eventos': eventos, 'f': f, 'filtros': FILTROS})


def detalle(request, pk):
    """Ficha del evento con RSVP (P-10), lista de espera (P-14) y muro (P-20)."""
    e = get_object_or_404(eventos_con_cupos(request.user), pk=pk)
    mi = None
    if request.user.is_authenticated:
        mi = e.inscripciones.filter(usuario=request.user).exclude(estado=Inscripcion.Estado.CANCELADA).first()
    coord_ids = {u.pk for u in e.comunidad.coordinadores()}
    return render(request, 'eventos/detalle.html', {
        'e': e, 'c': e.comunidad, 'mi': mi, 'form': MensajeForm(),
        'mensajes': e.mensajes.select_related('autor'),
        'coordinadores_ids': coord_ids, 'es_coord': request.user.pk in coord_ids,
        'motivos': Reporte.Motivo.choices,
    })


@login_required
@require_POST
def inscripcion(request, pk):
    """Un solo endpoint para inscribirse, cancelar o salir de la lista de espera."""
    e = get_object_or_404(Evento, pk=pk)
    accion = request.POST.get('accion')
    if accion == 'inscribir':
        try:
            insc = services.inscribir(e, request.user)
        except services.SinCupos:
            messages.error(request, 'No quedan cupos y este evento no tiene lista de espera.')
        else:
            if insc.estado == Inscripcion.Estado.CONFIRMADA:
                messages.success(request, f'Inscripción confirmada. Te esperamos el {timezone.localtime(e.inicio):%d/%m} a las {timezone.localtime(e.inicio):%H:%M}.')
            else:
                messages.success(request, f'Quedaste en la posición {insc.posicion_espera} de la lista de espera.')
    elif accion in ('cancelar', 'salir_espera'):
        promovido = services.cancelar(e, request.user)
        if accion == 'salir_espera':
            messages.success(request, 'Saliste de la lista de espera')
        elif promovido:
            messages.success(request, f'Cancelaste tu inscripción. {promovido.get_full_name()} pasó de la lista de espera al cupo y ya fue notificado.')
        else:
            messages.success(request, 'Cancelaste tu inscripción. El cupo quedó libre.')
    return redirect(request.POST.get('volver') or e.get_absolute_url())


@login_required
@require_POST
def confirmar(request, pk):
    """Respuesta a «¿Vas mañana?» (P-13)."""
    e = get_object_or_404(Evento, pk=pk)
    va = request.POST.get('va') == 'si'
    promovido = services.confirmar_asistencia(e, request.user, va)
    if va:
        messages.success(request, 'Asistencia confirmada. ¡Nos vemos!')
    elif promovido:
        messages.success(request, f'Liberaste tu cupo. {promovido.get_full_name()} pasó de la lista de espera.')
    else:
        messages.success(request, 'Liberaste tu cupo. Gracias por avisar.')
    return redirect(request.POST.get('volver') or 'core:inicio')


@login_required
@require_POST
def publicar_mensaje(request, pk):
    e = get_object_or_404(Evento, pk=pk)
    form = MensajeForm(request.POST)
    if form.is_valid():
        m = form.save(commit=False)
        m.autor, m.evento = request.user, e
        m.save()
        coords = e.comunidad.coordinadores()
        if request.user in coords:
            # Respuesta de coordinación: avisa a quienes preguntaron antes (P-18).
            previos = {x.autor for x in e.mensajes.exclude(autor__in=coords).select_related('autor')}
            notificar(previos, Notificacion.Tipo.RESPUESTA, f'Respondieron en {e.titulo}',
                      f'{request.user.get_full_name()}: “{m.texto[:120]}”', m.get_absolute_url())
        else:
            notificar(coords, Notificacion.Tipo.MENSAJE, f'Nueva consulta en {e.titulo}',
                      f'{request.user.get_full_name()}: “{m.texto[:120]}”', m.get_absolute_url())
        messages.success(request, 'Consulta publicada. La coordinación recibirá un aviso.')
    return redirect(e.get_absolute_url() + '#muro')


@login_required
def nuevo(request):
    """Publicar evento (P-09). Solo coordinación."""
    mis = comunidades_coordinadas(request.user).filter(estado='activa')
    if not mis.exists():
        raise PermissionDenied
    form = EventoForm(request.POST or None, comunidades=mis)
    if request.method == 'POST' and form.is_valid():
        e = form.save()
        integrantes = [m.usuario for m in e.comunidad.membresias.select_related('usuario').exclude(usuario=request.user)]
        notificar(integrantes, Notificacion.Tipo.MENSAJE, f'Nuevo evento: {e.titulo}',
                  f'{e.comunidad.nombre} publicó un evento.', e.get_absolute_url())
        messages.success(request, 'Evento publicado. Ya aparece en el feed de eventos.')
        return redirect(e)
    return render(request, 'eventos/form.html', {'form': form, 'comunidad': mis.first()})


@login_required
def mis_inscripciones(request):
    ahora = timezone.now()
    qs = eventos_con_cupos(request.user).filter(inicio__gte=ahora)
    return render(request, 'eventos/mis_inscripciones.html', {
        'confirmadas': qs.filter(mi_estado=Inscripcion.Estado.CONFIRMADA),
        'en_espera': qs.filter(mi_estado=Inscripcion.Estado.ESPERA),
    })
