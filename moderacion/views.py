from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from comunidades.models import Comunidad
from core.roles import staff_requerido
from eventos.models import Mensaje
from notificaciones.models import Notificacion
from notificaciones.services import notificar

from .models import Reporte


@login_required
@require_POST
def reportar(request, mensaje_id):
    """Reporte de mensaje inapropiado (P-35) + aviso a moderación (P-41)."""
    m = get_object_or_404(Mensaje, pk=mensaje_id, oculto=False)
    motivo = request.POST.get('motivo')
    if motivo not in Reporte.Motivo.values:
        messages.error(request, 'Elige un motivo para el reporte.')
    elif not Reporte.objects.filter(mensaje=m, reportado_por=request.user).exists():
        r = Reporte.objects.create(mensaje=m, reportado_por=request.user, motivo=motivo)
        donde = m.evento.titulo if m.evento_id else m.comunidad.nombre
        notificar(get_user_model().objects.filter(is_staff=True), Notificacion.Tipo.REPORTE,
                  'Nuevo contenido reportado', f'Un mensaje en “{donde}” fue reportado: {r.get_motivo_display().lower()}.',
                  '/moderacion/')
        messages.success(request, 'Reporte enviado. Administración lo revisará.')
    return redirect(m.get_absolute_url())


@staff_requerido
def panel(request):
    """Cola de reportes (P-39) y solicitudes de comunidades (P-21)."""
    inicio_mes = timezone.localdate().replace(day=1)
    return render(request, 'moderacion/panel.html', {
        'reportes': Reporte.objects.select_related('mensaje__autor', 'mensaje__evento', 'mensaje__comunidad', 'reportado_por')[:30],
        'solicitudes': Comunidad.objects.filter(estado=Comunidad.Estado.PENDIENTE).select_related('creada_por'),
        'n_pendientes': Reporte.objects.filter(estado=Reporte.Estado.PENDIENTE).count(),
        'n_resueltos': Reporte.objects.exclude(estado=Reporte.Estado.PENDIENTE).filter(resuelto_en__date__gte=inicio_mes).count(),
        'n_activas': Comunidad.objects.filter(estado=Comunidad.Estado.ACTIVA).count(),
    })


@staff_requerido
@require_POST
def resolver(request, pk):
    """Gestión de reportes (P-40)."""
    r = get_object_or_404(Reporte, pk=pk, estado=Reporte.Estado.PENDIENTE)
    ocultar = request.POST.get('accion') == 'ocultar'
    if ocultar:
        r.mensaje.oculto = True
        r.mensaje.save(update_fields=['oculto'])
    # Resuelve también otros reportes pendientes del mismo mensaje.
    Reporte.objects.filter(mensaje=r.mensaje, estado=Reporte.Estado.PENDIENTE).update(
        estado=Reporte.Estado.OCULTO if ocultar else Reporte.Estado.DESCARTADO,
        resuelto_por=request.user, resuelto_en=timezone.now())
    if ocultar:
        notificar(r.reportado_por, Notificacion.Tipo.REPORTE, 'Revisamos tu reporte',
                  'El mensaje que reportaste fue ocultado. Gracias por avisar.', r.mensaje.get_absolute_url())
    messages.success(request, 'Mensaje ocultado. Quien lo reportó recibirá un aviso.' if ocultar else 'Reporte descartado')
    return redirect('moderacion:panel')


@staff_requerido
@require_POST
def revisar_comunidad(request, pk):
    c = get_object_or_404(Comunidad, pk=pk, estado=Comunidad.Estado.PENDIENTE)
    if request.POST.get('accion') == 'aprobar':
        c.estado = Comunidad.Estado.ACTIVA
        c.save(update_fields=['estado'])
        if c.creada_por:
            notificar(c.creada_por, Notificacion.Tipo.SOLICITUD, f'{c.nombre} ya está publicada',
                      'Tu comunidad aparece en el directorio. Ya puedes publicar eventos.', c.get_absolute_url())
        messages.success(request, f'{c.nombre} ya aparece en el directorio')
    else:
        c.estado = Comunidad.Estado.OBSERVADA
        c.save(update_fields=['estado'])
        if c.creada_por:
            notificar(c.creada_por, Notificacion.Tipo.SOLICITUD, f'Falta información para publicar {c.nombre}',
                      'Completa la descripción y el lugar de reunión para que podamos publicarla.',
                      c.get_absolute_url() + 'editar/')
        messages.success(request, 'Se pidió más información a quien registró la comunidad')
    return redirect('moderacion:panel')
