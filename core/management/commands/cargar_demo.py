"""Carga datos de ejemplo para la demo. Uso: python manage.py cargar_demo

Las fechas se calculan desde hoy, así la demo siempre tiene eventos próximos.
Todos los usuarios de prueba tienen la contraseña «demo1234».
"""
import datetime
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from comunidades.models import Comunidad, Membresia
from eventos.models import Evento, Inscripcion, Mensaje
from moderacion.models import Reporte
from notificaciones.models import Notificacion

User = get_user_model()
CLAVE = 'demo1234'

PERSONAS = {
    # username: (nombre, apellido, staff)
    'valentina': ('Valentina', 'Rojas', False),
    'matias': ('Matías', 'Soto', False),
    'paula': ('Paula', 'Fuentes', True),
    'ignacio': ('Ignacio', 'Pérez', False), 'daniela': ('Daniela', 'Muñoz', False),
    'francisca': ('Francisca', 'Lagos', False), 'tomas': ('Tomás', 'Riquelme', False),
    'isidora': ('Isidora', 'Vera', False), 'benjamin': ('Benjamín', 'Araya', False),
    'camilo': ('Camilo', 'Herrera', False), 'antonia': ('Antonia', 'Céspedes', False),
    'javiera': ('Javiera', 'Ortiz', False), 'rocio': ('Rocío', 'Navarro', False),
}
NOMBRES = ['Camila', 'Diego', 'Fernanda', 'Joaquín', 'Sofía', 'Martín', 'Catalina', 'Lucas', 'Antonella', 'Vicente',
           'Florencia', 'Agustín', 'Josefa', 'Maximiliano', 'Constanza', 'Felipe', 'Emilia', 'Cristóbal', 'Trinidad', 'Gaspar']
APELLIDOS = ['González', 'Muñoz', 'Rojas', 'Díaz', 'Pérez', 'Soto', 'Contreras', 'Silva', 'Martínez', 'Sepúlveda',
             'Morales', 'Rodríguez', 'López', 'Fuentes', 'Hernández', 'Torres', 'Araya', 'Flores', 'Espinoza', 'Valenzuela']

COMUNIDADES = [
    # slug, nombre, tipo, categoria, desde, lugar, publicos, coordinadores, n_integrantes, descripcion
    ('ajedrez', 'Club de Ajedrez FCFM', 'oficial', 'juegos', '2011', 'Hall Sur, Beauchef 850', True, ['ignacio', 'daniela'], 30,
     'Entrenamientos semanales, torneos internos y simultáneas abiertas a toda la facultad. No necesitas saber jugar para venir.'),
    ('coro', 'Coro Beauchef', 'oficial', 'arte', '2004', 'Sala B-03', True, ['francisca'], 22,
     'Coro mixto de estudiantes, funcionarios y académicos. Ensayamos dos veces por semana y cantamos en las ceremonias de la facultad.'),
    ('escalada', 'Rama de Escalada', 'oficial', 'deporte', '2009', 'Gimnasio Beauchef', True, ['tomas', 'isidora'], 40,
     'Escalada en muro y salidas a roca en Las Chilcas y el Cajón del Maipo. Tenemos equipo para préstamo.'),
    ('huerta', 'Huerta Beauchef', 'emergente', 'ambiente', 'sep. 2026', 'Patio poniente', False, ['matias'], 16,
     'Grupo nuevo que quiere transformar el patio poniente en una huerta comunitaria con compostaje de los residuos del casino.'),
    ('mesa-de-rol', 'Mesa de Rol del 4° piso', 'emergente', 'juegos', 'ago. 2026', 'Sala 405 o Discord', True, ['benjamin'], 10,
     'Partidas one-shot y campañas cortas de rol. Rotamos sistemas: D&D, La Llamada de Cthulhu, Blades in the Dark.'),
    ('programacion-competitiva', 'Programación Competitiva', 'oficial', 'tecnologia', '2013', 'Laboratorio 3, Edificio Norte', True, ['camilo'], 45,
     'Preparación para ICPC y competencias nacionales. Contests de práctica cada sábado y clases de algoritmos.'),
    ('fotografia-analoga', 'Fotografía Análoga', 'emergente', 'arte', 'oct. 2026', 'Por definir', True, ['antonia'], 8,
     'Armamos un cuarto oscuro improvisado y compartimos químicos y rollos. Grupo recién formado, todas las cámaras sirven.'),
    ('matematicas-en-tu-liceo', 'Matemáticas en tu Liceo', 'oficial', 'voluntariado', '2015', 'Liceos de Santiago Centro', True, ['javiera'], 25,
     'Voluntariado de reforzamiento en matemáticas para liceos de Santiago Centro. Sábados por la mañana.'),
]

EVENTOS = [
    # clave, comunidad, titulo, dias desde hoy, hora, horas de duración, modalidad, lugar, cupos, inscritos, espera, descripcion
    ('ensayo', 'coro', 'Ensayo abierto: voces nuevas', 1, '17:30', 1.5, 'presencial', 'Sala B-03, Beauchef 851', 30, 19, 0,
     'Ensayo para quienes quieran probar el coro. Calentamos voz, aprendemos una pieza corta y conversamos sobre los ensayos del semestre.'),
    ('simultanea', 'ajedrez', 'Simultánea contra el campeón FCFM', 5, '18:00', 2.5, 'presencial', 'Hall Sur, Beauchef 850', 24, 24, 3,
     'Nuestro campeón interno juega 24 partidas a la vez. Trae tu propio tablero si tienes; si no, nosotros ponemos.'),
    ('muro', 'escalada', 'Iniciación en muro', 7, '10:00', 2.5, 'presencial', 'Gimnasio Beauchef', 12, 11, 0,
     'Primera vez en el muro: nudos básicos, aseguramiento y tres vías guiadas. Arnés y zapatillas incluidos.'),
    ('minga', 'huerta', 'Minga de compost', 10, '13:00', 1.5, 'presencial', 'Patio poniente', 20, 8, 0,
     'Armamos las primeras composteras con pallets donados. Trae guantes si tienes. Habrá once.'),
    ('oneshot', 'mesa-de-rol', 'One-shot: La Llamada de Cthulhu', 11, '19:00', 3.5, 'hibrido', 'Sala 405 + Discord', 6, 6, 1,
     'Partida autoconclusiva para principiantes. Personajes pregenerados. Cuatro asientos en sala y dos por Discord.'),
    ('revelado', 'fotografia-analoga', 'Revelado en blanco y negro', 12, '16:00', 2, 'presencial', 'Sala 210 (cuarto oscuro temporal)', 8, 3, 0,
     'Revelamos rollos de 35 mm. Si no tienes rollo, trae ganas: hay químicos para todos.'),
    ('contest', 'programacion-competitiva', 'Contest de práctica ICPC', 14, '15:00', 5, 'remoto', 'Enlace en Codeforces al inscribirte', 80, 52, 0,
     'Cinco horas, problemas de la regional 2025. Equipos de tres o individual.'),
]


class Command(BaseCommand):
    help = 'Borra los datos de la app y carga la demo (usuarios, comunidades, eventos, mensajes y reportes).'

    @transaction.atomic
    def handle(self, *args, **opts):
        for M in (Reporte, Notificacion, Mensaje, Inscripcion, Evento, Membresia, Comunidad):
            M.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.clave = make_password(CLAVE)  # se calcula una vez: hashear 70 veces es lento
        u = {}
        for username, (nom, ape, staff) in PERSONAS.items():
            u[username] = self._usuario(username, nom, ape, staff)
        relleno = []
        for i in range(60):
            nom, ape = NOMBRES[i % 20], APELLIDOS[(i * 7) % 20]
            relleno.append(self._usuario(f'estudiante{i + 1:02d}', nom, ape, False))
        u['valentina'].email = 'valentina.rojas@ug.uchile.cl'
        u['valentina'].save()

        com = {}
        for slug, nombre, tipo, cat, desde, lugar, pub, coords, n_int, desc in COMUNIDADES:
            c = Comunidad.objects.create(slug=slug, nombre=nombre, tipo=tipo, categoria=cat, activa_desde=desde,
                                         lugar=lugar, integrantes_publicos=pub, descripcion=desc,
                                         estado=Comunidad.Estado.ACTIVA, creada_por=u[coords[0]])
            for k in coords:
                Membresia.objects.create(usuario=u[k], comunidad=c, rol=Membresia.Rol.COORDINADOR)
            for p in relleno[(len(com) * 5):(len(com) * 5) + n_int]:
                Membresia.objects.create(usuario=p, comunidad=c)
            com[slug] = c
        Membresia.objects.create(usuario=u['valentina'], comunidad=com['coro'])

        hoy = timezone.localdate()
        tz = timezone.get_current_timezone()
        ev = {}
        for clave, slug, titulo, dias, hora, dur, modo, lugar, cupos, n_ins, n_esp, desc in EVENTOS:
            h, m = map(int, hora.split(':'))
            inicio = timezone.make_aware(datetime.datetime.combine(hoy + timedelta(days=dias), datetime.time(h, m)), tz)
            e = Evento.objects.create(comunidad=com[slug], titulo=titulo, descripcion=desc, inicio=inicio,
                                      fin=inicio + timedelta(hours=dur), modalidad=modo, lugar=lugar, cupos=cupos)
            gente = relleno[::-1] if clave == 'contest' else relleno
            inscritos = gente[:n_ins]
            if clave == 'ensayo':
                inscritos = gente[:n_ins - 1] + [u['valentina']]
            for p in inscritos:
                Inscripcion.objects.create(evento=e, usuario=p, estado=Inscripcion.Estado.CONFIRMADA)
            for p in gente[n_ins:n_ins + n_esp]:
                Inscripcion.objects.create(evento=e, usuario=p, estado=Inscripcion.Estado.ESPERA)
            ev[clave] = e

        ahora = timezone.now()

        def msg(autor, texto, evento=None, comunidad=None, horas=1):
            m = Mensaje.objects.create(autor=autor, texto=texto, evento=evento, comunidad=comunidad)
            Mensaje.objects.filter(pk=m.pk).update(creado=ahora - timedelta(hours=horas))  # antigüedad realista
            return m

        msg(u['francisca'], 'Recuerden traer agua. Las partituras las imprimimos nosotros.', ev['ensayo'], horas=48)
        msg(relleno[3], '¿Hay que saber leer partitura para ir?', ev['ensayo'], horas=30)
        msg(u['francisca'], 'Para nada. Aprendemos de oído la primera vez.', ev['ensayo'], horas=26)
        msg(relleno[6], '¿Se puede llegar a las 18:30 o ya parten todas las partidas juntas?', ev['simultanea'], horas=3)
        msg(u['ignacio'], 'Parten todas a las 18:00 en punto. Si no alcanzas, avisa y liberamos tu tablero para la lista de espera.', ev['simultanea'], horas=2)
        msg(u['matias'], 'Conseguimos 10 pallets. Faltan tornillos de 2", si alguien tiene que avise.', ev['minga'], horas=5)
        ofensivo = msg(relleno[40], 'compren los tornillos ustedes, para qué piden cosas gratis xd', ev['minga'], horas=1)
        spam = msg(relleno[41], 'Vendo apuntes de Cálculo II y Física a $5.000, escríbanme al interno', ev['oneshot'], horas=3)
        acoso = msg(relleno[42], 'Si les va mal es porque son flojos, no hay otra explicación', ev['contest'], horas=20)
        msg(u['matias'], 'Bienvenidos. Estamos esperando respuesta de la Dirección Económica para usar el patio poniente.', comunidad=com['huerta'], horas=24)
        msg(relleno[2], 'Puedo conseguir semillas de lechuga y cilantro en el vivero de mi comuna.', comunidad=com['huerta'], horas=22)
        msg(u['francisca'], 'Subimos las grabaciones del concierto de septiembre a la carpeta compartida.', comunidad=com['coro'], horas=96)

        for m, quien, motivo, horas in [(ofensivo, relleno[2], Reporte.Motivo.OFENSIVO, 0.8),
                                        (spam, u['benjamin'], Reporte.Motivo.SPAM, 2.5),
                                        (acoso, u['camilo'], Reporte.Motivo.ACOSO, 19)]:
            r = Reporte.objects.create(mensaje=m, reportado_por=quien, motivo=motivo)
            Reporte.objects.filter(pk=r.pk).update(creado=ahora - timedelta(hours=horas))

        Comunidad.objects.create(nombre='Taller de Cerámica', tipo='emergente', categoria='arte',
                                 descripcion='Buscamos un horno compartido y un espacio para trabajar arcilla los viernes.',
                                 lugar='Por definir', estado=Comunidad.Estado.PENDIENTE, creada_por=u['rocio'])

        N = Notificacion.Tipo
        e = ev['ensayo']
        for tipo, titulo, texto, url, leida in [
            (N.RESUMEN, 'Tu día en Beauchef', 'Hoy no tienes actividades. Hay 3 eventos con cupos disponibles esta semana.', '/eventos/', True),
            (N.RESPUESTA, 'Respondieron en Ensayo abierto: voces nuevas', 'Francisca Lagos: “Para nada. Aprendemos de oído la primera vez.”', e.get_absolute_url() + '#muro', True),
            (N.MENSAJE, 'Nuevo mensaje en Simultánea contra el campeón FCFM', 'Ignacio Pérez respondió en el muro del evento.', ev['simultanea'].get_absolute_url() + '#muro', False),
            (N.CONFIRMACION, f'Confirma tu asistencia: {e.titulo}', 'Es mañana. Si no puedes ir, libera tu cupo para alguien en lista de espera.', e.get_absolute_url(), False),
        ]:
            Notificacion.objects.create(usuario=u['valentina'], tipo=tipo, titulo=titulo, texto=texto, url=url, leida=leida)
        Notificacion.objects.create(usuario=u['matias'], tipo=N.SOLICITUD, titulo='Nuevo integrante en Huerta Beauchef',
                                    texto='Lucas se unió a la comunidad.', url=com['huerta'].get_absolute_url() + '?tab=integrantes')
        for titulo, texto in [('Nuevo contenido reportado', 'Un mensaje en “Minga de compost” fue reportado por lenguaje ofensivo.'),
                              ('Solicitud de nueva comunidad: Taller de Cerámica', 'Rocío Navarro quiere registrar “Taller de Cerámica”.')]:
            Notificacion.objects.create(usuario=u['paula'], tipo=N.REPORTE if 'reportado' in titulo else N.SOLICITUD,
                                        titulo=titulo, texto=texto, url='/moderacion/')

        self.stdout.write(self.style.SUCCESS(
            'Demo cargada. Usuarios: valentina (estudiante), matias (coordinador), paula (administración). '
            f'Contraseña: {CLAVE}'))

    def _usuario(self, username, nombre, apellido, staff):
        user = User(username=username, first_name=nombre, last_name=apellido, is_staff=staff,
                    email=f'{username}@ug.uchile.cl')
        user.password = self.clave
        user.save()
        return user
