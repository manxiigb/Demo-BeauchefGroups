from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from eventos.models import Inscripcion

from .models import Notificacion


@login_required
def lista(request):
    notifs = list(request.user.notificaciones.all()[:40])
    # Para mostrar los botones «Sí, voy / No podré ir» solo si aún falta responder.
    pendientes = set(Inscripcion.objects.filter(
        usuario=request.user, estado=Inscripcion.Estado.CONFIRMADA, confirmo_asistencia__isnull=True
    ).values_list('evento_id', flat=True))
    for n in notifs:
        n.evento_id = None
        if n.tipo == Notificacion.Tipo.CONFIRMACION and n.url.startswith('/eventos/'):
            try:
                pk = int(n.url.strip('/').split('/')[1])
            except (IndexError, ValueError):
                continue
            n.evento_id = pk if pk in pendientes else None
    return render(request, 'notificaciones/lista.html', {'notificaciones': notifs})


@login_required
def abrir(request, pk):
    n = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    n.leida = True
    n.save(update_fields=['leida'])
    return redirect(n.url or 'notificaciones:lista')


@login_required
@require_POST
def marcar_todas(request):
    request.user.notificaciones.filter(leida=False).update(leida=True)
    messages.success(request, 'Todas marcadas como leídas')
    return redirect('notificaciones:lista')
