from django.urls import path

from . import views

app_name = 'eventos'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('nuevo/', views.nuevo, name='nuevo'),
    path('mis-inscripciones/', views.mis_inscripciones, name='mis_inscripciones'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/inscripcion/', views.inscripcion, name='inscripcion'),
    path('<int:pk>/confirmar/', views.confirmar, name='confirmar'),
    path('<int:pk>/mensajes/', views.publicar_mensaje, name='publicar_mensaje'),
]
