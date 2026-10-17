from django.urls import path

from . import views

app_name = 'comunidades'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('nueva/', views.nueva, name='nueva'),
    path('<slug:slug>/', views.detalle, name='detalle'),
    path('<slug:slug>/editar/', views.editar, name='editar'),
    path('<slug:slug>/unirse/', views.unirse, name='unirse'),
    path('<slug:slug>/salir/', views.salir, name='salir'),
    path('<slug:slug>/foro/', views.publicar_foro, name='publicar_foro'),
]
