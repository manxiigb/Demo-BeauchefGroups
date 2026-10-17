"""Reglas de negocio de inscripciones. Las vistas solo llaman estas funciones."""
from django.db import transaction

from notificaciones.models import Notificacion
from notificaciones.services import notificar

from .models import Evento, Inscripcion


class SinCupos(Exception):
    pass


def _bloquear(evento):
    # Bloquea la fila del evento para que dos inscripciones simultáneas no tomen el mismo cupo.
    return Evento.objects.select_for_update().get(pk=evento.pk)


@transaction.atomic
def inscribir(evento, usuario):
    """Toma un cupo libre o, si no hay, entra a la lista de espera (P-10, P-14)."""
    evento = _bloquear(evento)
    insc = Inscripcion.objects.filter(evento=evento, usuario=usuario).first()
    if insc and insc.estado != Inscripcion.Estado.CANCELADA:
        return insc
    if evento.libres > 0:
        estado = Inscripcion.Estado.CONFIRMADA
    elif evento.lista_espera:
        estado = Inscripcion.Estado.ESPERA
    else:
        raise SinCupos
    if insc:
        # Vuelve a inscribirse: se borra y recrea para quedar al final de la lista.
        insc.delete()
    return Inscripcion.objects.create(evento=evento, usuario=usuario, estado=estado)


@transaction.atomic
def cancelar(evento, usuario):
    """Cancela la inscripción. Si liberó un cupo, promueve a la primera persona en espera.
    Devuelve el usuario promovido o None."""
    evento = _bloquear(evento)
    insc = Inscripcion.objects.filter(evento=evento, usuario=usuario).exclude(
        estado=Inscripcion.Estado.CANCELADA).first()
    if not insc:
        return None
    liberaba_cupo = insc.estado == Inscripcion.Estado.CONFIRMADA
    insc.estado = Inscripcion.Estado.CANCELADA
    insc.save(update_fields=['estado', 'actualizada'])
    if not liberaba_cupo:
        return None
    return promover_espera(evento)


def promover_espera(evento):
    siguiente = (Inscripcion.objects.select_for_update()
                 .filter(evento=evento, estado=Inscripcion.Estado.ESPERA)
                 .order_by('creada').first())
    if not siguiente:
        return None
    siguiente.estado = Inscripcion.Estado.CONFIRMADA
    siguiente.save(update_fields=['estado', 'actualizada'])
    notificar(siguiente.usuario, Notificacion.Tipo.CUPO,
              f'Tienes cupo en {evento.titulo}',
              'Se liberó un lugar y pasaste de la lista de espera a inscrito.',
              evento.get_absolute_url())
    return siguiente.usuario


def confirmar_asistencia(evento, usuario, va):
    """Respuesta a la confirmación dinámica (P-13). Si no va, libera el cupo."""
    insc = Inscripcion.objects.filter(evento=evento, usuario=usuario,
                                      estado=Inscripcion.Estado.CONFIRMADA).first()
    if not insc:
        return None
    Notificacion.objects.filter(usuario=usuario, tipo=Notificacion.Tipo.CONFIRMACION,
                                url=evento.get_absolute_url()).update(leida=True)
    if va:
        insc.confirmo_asistencia = True
        insc.save(update_fields=['confirmo_asistencia', 'actualizada'])
        return None
    return cancelar(evento, usuario)
