from django.urls import path

from . import views

app_name = 'moderacion'
urlpatterns = [
    path('', views.panel, name='panel'),
    path('reportes/<int:pk>/resolver/', views.resolver, name='resolver'),
    path('comunidades/<int:pk>/revisar/', views.revisar_comunidad, name='revisar_comunidad'),
    path('mensajes/<int:mensaje_id>/reportar/', views.reportar, name='reportar'),
]
