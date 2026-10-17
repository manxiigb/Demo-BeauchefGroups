from django.conf import settings
from django.db import models

from eventos.models import Mensaje


class Reporte(models.Model):
    """Reporte de mensaje inapropiado (P-35) y su resolución (P-40)."""

    class Motivo(models.TextChoices):
        OFENSIVO = 'ofensivo', 'Lenguaje ofensivo o burla'
        ACOSO = 'acoso', 'Acoso o descalificación'
        SPAM = 'spam', 'Spam o publicidad'
        FALSO = 'falso', 'Información falsa sobre el evento'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        OCULTO = 'oculto', 'Mensaje ocultado'
        DESCARTADO = 'descartado', 'Reporte descartado'

    mensaje = models.ForeignKey(Mensaje, on_delete=models.CASCADE, related_name='reportes')
    reportado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reportes_hechos')
    motivo = models.CharField(max_length=10, choices=Motivo.choices)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    creado = models.DateTimeField(auto_now_add=True)
    resuelto_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='reportes_resueltos')
    resuelto_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['estado', '-creado']

    def __str__(self):
        return f'{self.get_motivo_display()}: {self.mensaje}'

    @property
    def grave(self):
        return self.motivo == self.Motivo.ACOSO
