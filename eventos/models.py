from django.conf import settings
from django.db import models
from django.urls import reverse

from comunidades.models import Comunidad


class Evento(models.Model):
    """Actividad publicada por una comunidad (P-09, P-15)."""

    class Modalidad(models.TextChoices):
        PRESENCIAL = 'presencial', 'Presencial'
        REMOTO = 'remoto', 'Remoto'
        HIBRIDO = 'hibrido', 'Híbrido'

    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='eventos')
    titulo = models.CharField('Nombre del evento', max_length=80)
    descripcion = models.TextField('Descripción', blank=True)
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    modalidad = models.CharField(max_length=10, choices=Modalidad.choices, default=Modalidad.PRESENCIAL)
    lugar = models.CharField('Lugar o enlace', max_length=150)
    cupos = models.PositiveIntegerField(default=20)
    lista_espera = models.BooleanField('Activar lista de espera automática', default=True)
    pedir_confirmacion = models.BooleanField('Pedir confirmación de asistencia 24 horas antes', default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['inicio']

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('eventos:detalle', args=[self.pk])

    # --- cupos ---
    @property
    def inscritos(self):
        if hasattr(self, 'n_inscritos'):  # anotado en la consulta
            return self.n_inscritos
        return self.inscripciones.filter(estado=Inscripcion.Estado.CONFIRMADA).count()

    @property
    def en_espera(self):
        if hasattr(self, 'n_espera'):
            return self.n_espera
        return self.inscripciones.filter(estado=Inscripcion.Estado.ESPERA).count()

    @property
    def libres(self):
        return max(0, self.cupos - self.inscritos)

    @property
    def nivel_cupos(self):
        """ok / warn / bad, para colorear el estado de cupos."""
        if self.libres == 0:
            return 'bad'
        return 'warn' if self.libres <= 3 else 'ok'

    @property
    def porcentaje(self):
        return round(self.inscritos / self.cupos * 100) if self.cupos else 100


class Inscripcion(models.Model):
    """RSVP de un estudiante (P-10) y su lugar en lista de espera (P-14)."""

    class Estado(models.TextChoices):
        CONFIRMADA = 'confirmada', 'Confirmada'
        ESPERA = 'espera', 'En lista de espera'
        CANCELADA = 'cancelada', 'Cancelada'

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='inscripciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inscripciones')
    estado = models.CharField(max_length=10, choices=Estado.choices)
    confirmo_asistencia = models.BooleanField(null=True, blank=True)  # P-13
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('evento', 'usuario')]
        ordering = ['creada']
        verbose_name_plural = 'inscripciones'

    def __str__(self):
        return f'{self.usuario} → {self.evento} ({self.estado})'

    @property
    def posicion_espera(self):
        if self.estado != self.Estado.ESPERA:
            return None
        return self.evento.inscripciones.filter(
            estado=self.Estado.ESPERA, creada__lt=self.creada).count() + 1


class Mensaje(models.Model):
    """Mensaje del muro de un evento (P-20) o del foro de una comunidad (P-33)."""

    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mensajes')
    evento = models.ForeignKey(Evento, null=True, blank=True, on_delete=models.CASCADE, related_name='mensajes')
    comunidad = models.ForeignKey(Comunidad, null=True, blank=True, on_delete=models.CASCADE, related_name='mensajes_foro')
    texto = models.TextField(max_length=1000)
    oculto = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado']
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(evento__isnull=False, comunidad__isnull=True) |
                           models.Q(evento__isnull=True, comunidad__isnull=False)),
                name='mensaje_en_evento_o_foro'),
        ]

    def __str__(self):
        return self.texto[:50]

    @property
    def comunidad_de_origen(self):
        return self.evento.comunidad if self.evento_id else self.comunidad

    def get_absolute_url(self):
        if self.evento_id:
            return self.evento.get_absolute_url() + '#muro'
        return self.comunidad.get_absolute_url() + '?tab=foro'
