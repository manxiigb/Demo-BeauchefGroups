from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from comunidades.models import Comunidad
from moderacion.models import Reporte
from notificaciones.models import Notificacion

from .models import Evento, Inscripcion

User = get_user_model()


class DemoTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_demo', stdout=StringIO())

    def entrar(self, username):
        self.client.force_login(User.objects.get(username=username))


class PaginasTest(DemoTestCase):
    def test_todas_las_paginas_cargan_para_cada_perfil(self):
        e = Evento.objects.get(titulo__startswith='Simultánea')
        urls = ['/', '/comunidades/', '/comunidades/?tipo=emergente&cat=arte&q=a', '/comunidades/huerta/',
                '/comunidades/huerta/?tab=foro', '/comunidades/huerta/?tab=integrantes', '/eventos/', '/eventos/?f=cupos',
                e.get_absolute_url(), '/cuentas/ingresar/', '/mapa-django/']
        for quien in [None, 'valentina', 'matias', 'paula']:
            self.client.logout()
            if quien:
                self.entrar(quien)
            for url in urls:
                with self.subTest(quien=quien, url=url):
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_permisos(self):
        self.entrar('valentina')
        self.assertEqual(self.client.get('/moderacion/').status_code, 403)
        self.assertEqual(self.client.get('/eventos/nuevo/').status_code, 403)
        self.entrar('matias')
        self.assertEqual(self.client.get('/eventos/nuevo/').status_code, 200)
        self.entrar('paula')
        self.assertEqual(self.client.get('/moderacion/').status_code, 200)

    def test_integrantes_privados(self):
        self.entrar('valentina')
        r = self.client.get('/comunidades/huerta/?tab=integrantes')
        self.assertContains(r, 'lista de integrantes privada')


class ListaEsperaTest(DemoTestCase):
    def test_cancelar_promueve_al_primero_en_espera(self):
        e = Evento.objects.get(titulo__startswith='Simultánea')
        primero = e.inscripciones.filter(estado='espera').order_by('creada').first().usuario
        inscrito = e.inscripciones.filter(estado='confirmada').first().usuario
        self.client.force_login(inscrito)
        self.client.post(reverse('eventos:inscripcion', args=[e.pk]), {'accion': 'cancelar'})
        self.assertEqual(Inscripcion.objects.get(evento=e, usuario=primero).estado, 'confirmada')
        self.assertEqual(e.inscritos, 24)
        self.assertTrue(Notificacion.objects.filter(usuario=primero, tipo='cupo').exists())

    def test_inscribir_en_evento_lleno_entra_a_espera(self):
        e = Evento.objects.get(titulo__startswith='Simultánea')
        self.entrar('valentina')
        self.client.post(reverse('eventos:inscripcion', args=[e.pk]), {'accion': 'inscribir'})
        insc = Inscripcion.objects.get(evento=e, usuario__username='valentina')
        self.assertEqual(insc.estado, 'espera')
        self.assertEqual(insc.posicion_espera, 4)

    def test_no_podre_ir_libera_cupo(self):
        e = Evento.objects.get(titulo__startswith='Ensayo')
        self.entrar('valentina')
        r = self.client.get('/')
        self.assertContains(r, '¿Vas a Ensayo abierto')
        self.client.post(reverse('eventos:confirmar', args=[e.pk]), {'va': 'no'})
        self.assertEqual(Inscripcion.objects.get(evento=e, usuario__username='valentina').estado, 'cancelada')


class FlujosTest(DemoTestCase):
    def test_crear_evento(self):
        self.entrar('matias')
        huerta = Comunidad.objects.get(slug='huerta')
        r = self.client.post('/eventos/nuevo/', {
            'comunidad': huerta.pk, 'titulo': 'Siembra de almácigos', 'fecha': '2030-11-03',
            'hora_inicio': '13:00', 'hora_fin': '14:30', 'modalidad': 'presencial', 'lugar': 'Patio poniente',
            'cupos': 15, 'descripcion': 'x', 'lista_espera': 'on'})
        e = Evento.objects.get(titulo='Siembra de almácigos')
        self.assertRedirects(r, e.get_absolute_url())

    def test_registrar_y_aprobar_comunidad(self):
        self.entrar('valentina')
        self.client.post('/comunidades/nueva/', {'nombre': 'Club de Astronomía', 'tipo': 'emergente',
                                                 'categoria': 'tecnologia', 'descripcion': 'Miramos el cielo.',
                                                 'lugar': 'Azotea', 'integrantes_publicos': 'True'})
        c = Comunidad.objects.get(nombre='Club de Astronomía')
        self.assertEqual(c.estado, 'pendiente')
        self.entrar('paula')
        self.client.post(reverse('moderacion:revisar_comunidad', args=[c.pk]), {'accion': 'aprobar'})
        c.refresh_from_db()
        self.assertEqual(c.estado, 'activa')

    def test_reportar_y_ocultar(self):
        e = Evento.objects.get(titulo__startswith='Ensayo')
        m = e.mensajes.exclude(autor__username='francisca').first()
        self.entrar('valentina')
        self.client.post(reverse('moderacion:reportar', args=[m.pk]), {'motivo': 'spam'})
        r = Reporte.objects.get(mensaje=m)
        self.entrar('paula')
        self.client.post(reverse('moderacion:resolver', args=[r.pk]), {'accion': 'ocultar'})
        m.refresh_from_db()
        self.assertTrue(m.oculto)
