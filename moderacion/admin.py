from django.contrib import admin

from .models import Reporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['mensaje', 'motivo', 'estado', 'reportado_por', 'creado']
    list_filter = ['estado', 'motivo']
