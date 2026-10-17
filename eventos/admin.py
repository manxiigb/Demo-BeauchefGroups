from django.contrib import admin

from .models import Evento, Inscripcion, Mensaje


class InscripcionInline(admin.TabularInline):
    model = Inscripcion
    extra = 0
    autocomplete_fields = ['usuario']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'comunidad', 'inicio', 'modalidad', 'cupos']
    list_filter = ['modalidad', 'comunidad']
    search_fields = ['titulo']
    inlines = [InscripcionInline]


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['texto', 'autor', 'evento', 'comunidad', 'oculto', 'creado']
    list_filter = ['oculto']
