"""Etiquetas de interfaz: {% icono 'home' %}, {% pi 'P-10 / I1' %}, {{ nombre|iniciales }}."""
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

ICONOS = {
    'home': '<path d="M3 10.5 10 4l7 6.5V17a1 1 0 0 1-1 1h-4v-5H8v5H4a1 1 0 0 1-1-1z"/>',
    'users': '<circle cx="7" cy="7" r="3"/><circle cx="14.5" cy="8" r="2.4"/><path d="M1.8 17c.5-3 2.6-4.6 5.2-4.6s4.7 1.6 5.2 4.6M12.6 12.7c2.4-.3 4.6 1 5.2 4.3"/>',
    'cal': '<rect x="3" y="4.5" width="14" height="12.5" rx="2"/><path d="M3 8.5h14M7 2.5v4M13 2.5v4"/>',
    'ticket': '<path d="M3 6a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v2a2 2 0 0 0 0 4v2a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-2a2 2 0 0 0 0-4z"/><path d="M12 5v10" stroke-dasharray="1.5 2"/>',
    'bell': '<path d="M5 8a5 5 0 0 1 10 0c0 4 1.5 5.5 1.5 5.5h-13S5 12 5 8M8.3 16.5a1.8 1.8 0 0 0 3.4 0"/>',
    'plus': '<circle cx="10" cy="10" r="7.5"/><path d="M10 6.5v7M6.5 10h7"/>',
    'flag': '<path d="M4.5 17.5V3.5M4.5 4h9.5l-2 3.5 2 3.5H4.5"/>',
    'sprout': '<path d="M10 17.5V10M10 10C10 6 7 4 3.5 4c0 4 2.5 6 6.5 6M10 12c0-3.5 2.6-5.5 6.5-5.5 0 3.6-2.6 5.5-6.5 5.5"/>',
    'shield': '<path d="M10 2.5 16.5 5v5c0 4-3 6.6-6.5 7.5C6.5 16.6 3.5 14 3.5 10V5z"/>',
    'clock': '<circle cx="10" cy="10" r="7.5"/><path d="M10 6v4.3l2.8 1.7"/>',
    'msg': '<path d="M3.5 4.5h13v9h-7l-4 3v-3h-2z"/>',
    'check': '<path d="m4.5 10.5 3.5 3.5 7.5-8"/>',
    'search': '<circle cx="9" cy="9" r="5.5"/><path d="m13 13 4 4"/>',
    'out': '<path d="M8 3.5H4.5v13H8M12 6.5 15.5 10 12 13.5M15.5 10H8"/>',
}


@register.simple_tag
def icono(nombre, tam=None, grosor='1.8', estilo=''):
    tam_attr = f' width="{tam}" height="{tam}"' if tam else ''
    style = f' style="stroke:currentColor;fill:none;stroke-width:{grosor};stroke-linecap:round;stroke-linejoin:round;flex:none;{estilo}"' if tam else ''
    return mark_safe(f'<svg viewBox="0 0 20 20"{tam_attr}{style} aria-hidden="true">{ICONOS.get(nombre, "")}</svg>')


@register.simple_tag
def pi(texto):
    """Código del post-it del tablero; visible solo con la casilla «Post-its del tablero»."""
    return format_html('<span class="pi">{}</span>', texto)


@register.filter
def iniciales(nombre):
    partes = [p for p in str(nombre).split() if p and p[0].isalnum()]
    return ''.join(p[0] for p in partes[:2]).upper()


@register.filter
def rango(n):
    return range(int(n))
