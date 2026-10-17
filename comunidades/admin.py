from django.contrib import admin

from .models import Comunidad, Membresia


class MembresiaInline(admin.TabularInline):
    model = Membresia
    extra = 0
    autocomplete_fields = ['usuario']


@admin.register(Comunidad)
class ComunidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'categoria', 'estado']
    list_filter = ['tipo', 'categoria', 'estado']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ['nombre']}
    inlines = [MembresiaInline]
