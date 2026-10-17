from django.db.models import Count, OuterRef, Q, Subquery

from .models import Evento, Inscripcion


def eventos_con_cupos(user=None):
    """Eventos de comunidades activas con conteos anotados y el estado de inscripción del usuario."""
    qs = (Evento.objects.filter(comunidad__estado='activa').select_related('comunidad')
          .annotate(n_inscritos=Count('inscripciones', filter=Q(inscripciones__estado=Inscripcion.Estado.CONFIRMADA)),
                    n_espera=Count('inscripciones', filter=Q(inscripciones__estado=Inscripcion.Estado.ESPERA))))
    if user is not None and user.is_authenticated:
        mia = Inscripcion.objects.filter(evento=OuterRef('pk'), usuario=user).exclude(
            estado=Inscripcion.Estado.CANCELADA).values('estado')[:1]
        qs = qs.annotate(mi_estado=Subquery(mia))
    return qs.order_by('inicio')
