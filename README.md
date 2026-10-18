# Comunidades Beauchef · Demo (Grupo 16, CC4402)

App para descubrir GG.OO. y grupos emergentes de la FCFM, inscribirse a sus eventos con cupos y lista de espera, conversar en muros y foros, y moderar contenido. Implementa en Django el prototipo clickeable de la Tarea 2.

## Cómo correrlo (Windows, PowerShell)

```powershell
cd ~\Demo-BeauchefGroups
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

Abre http://127.0.0.1:8000. La barra morada de arriba permite cambiar de perfil sin contraseña:

| Perfil | Usuario | Qué puede hacer |
|---|---|---|
| Visitante | (sin sesión) | Ver el directorio y los eventos |
| Estudiante | `valentina` | Inscribirse, lista de espera, confirmar asistencia, muros, reportar |
| Coordinador | `matias` (Huerta Beauchef) | Lo anterior + publicar eventos y editar la ficha |
| Administrador | `paula` | Moderación de reportes y aprobación de comunidades |

Todos los usuarios de prueba usan la contraseña `demo1234`. Para entrar a `/admin/` crea un superusuario con `python manage.py createsuperuser`.

`cargar_demo` borra los datos de la app y los vuelve a crear con fechas calculadas desde hoy. Úsalo antes de cada presentación.

## Estructura

```
config/          settings y urls del proyecto
core/            inicio, ingreso, barra de demo, roles, etiquetas de plantilla, comando cargar_demo
comunidades/     Comunidad, Membresia · directorio, ficha, registro, foro
eventos/         Evento, Inscripcion, Mensaje · feed, ficha, RSVP, muro
  services.py    reglas de inscripción y lista de espera (con bloqueo de fila)
moderacion/      Reporte · reportar mensaje, panel de moderación
notificaciones/  Notificacion · lista de avisos
templates/       base.html, includes/ (parciales reutilizables) y una carpeta por app
static/          css/app.css (diseño del prototipo) y js/app.js (mínimo)
```

La página **Mapa Django** (enlace en la barra morada) lista qué vista, plantilla y modelos hay detrás de cada pantalla.

## Post-its cubiertos

| Incremento | Post-its |
|---|---|
| I1 (MVP) | Home y navegación, P-32 ficha de comunidad, P-09 crear evento, P-10 RSVP, P-12 ingreso (simulado), P-34 directorio, P-15 eventos próximos, P-16 ficha de grupo |
| I2 | P-33 foro, P-14 lista de espera automática, P-20 muro del evento, P-13 confirmación de asistencia, P-19 aviso de nuevo mensaje |
| I3 | P-35 reportar mensaje, P-40 gestión de reportes, P-39 cola de moderación, P-18 aviso de respuesta, P-21 solicitudes, P-41 aviso de reporte |

Pendiente: OAuth real de la U. de Chile (P-12), tareas programadas para recordatorios T-24h/T-2h y resumen matutino (P-17, P-22), envío push o correo (P-36), PostgreSQL y despliegue.

## Pruebas

```powershell
python manage.py test
```
