from django.urls import path

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('cuentas/ingresar/', views.ingresar, name='login'),
    path('cuentas/salir/', views.salir, name='logout'),
    path('demo/como/', views.demo_como, name='demo_como'),
    path('mapa-django/', views.mapa_django, name='mapa_django'),
]
