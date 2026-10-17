from django.conf import settings
from django.db import models


class Notificacion(models.Model):
    class Tipo(models.TextChoices):
        CONFIRMACION = 'confirmacion', 'Confirmación de asistencia'   # P-13
        RECORDATORIO = 'recordatorio', 'Recordatorio de evento'       # P-17
        RESPUESTA = 'respuesta', 'Respuesta a tu mensaje'             # P-18
        MENSAJE = 'mensaje', 'Nuevo mensaje'                          # P-19
        SOLICITUD = 'solicitud', 'Solicitud'                          # P-21
        RESUMEN = 'resumen', 'Resumen del día'                        # P-22
        CUPO = 'cupo', 'Cupo asignado'                                # P-14
        REPORTE = 'reporte', 'Contenido reportado'                    # P-41

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=15, choices=Tipo.choices)
    titulo = models.CharField(max_length=140)
    texto = models.CharField(max_length=300, blank=True)
    url = models.CharField(max_length=200, blank=True)
    leida = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada']
        verbose_name_plural = 'notificaciones'

    def __str__(self):
        return self.titulo

    @property
    def icono(self):
        return {'confirmacion': 'clock', 'recordatorio': 'clock', 'respuesta': 'msg', 'mensaje': 'msg',
                'solicitud': 'sprout', 'resumen': 'cal', 'cupo': 'check', 'reporte': 'flag'}[self.tipo]

    @property
    def tono(self):
        return {'confirmacion': 'warn', 'recordatorio': 'warn', 'cupo': 'ok', 'resumen': 'ok',
                'reporte': 'bad', 'solicitud': 'warn'}.get(self.tipo, '')
