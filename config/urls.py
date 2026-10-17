"""Rutas del proyecto. Cada app tiene su propio urls.py (ver /mapa-django/)."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('comunidades/', include('comunidades.urls')),
    path('eventos/', include('eventos.urls')),
    path('moderacion/', include('moderacion.urls')),
    path('notificaciones/', include('notificaciones.urls')),
    path('', include('core.urls')),
]
