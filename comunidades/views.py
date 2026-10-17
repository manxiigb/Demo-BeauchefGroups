from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from eventos.forms import MensajeForm
from eventos.queries import eventos_con_cupos
from moderacion.models import Reporte
from notificaciones.models import Notificacion
from notificaciones.services import notificar

from .forms import ComunidadForm
from .models import Comunidad, Membresia


def lista(request):
    """Directorio con buscador y filtros (P-34)."""
    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', 'todas')
    cat = request.GET.get('cat', '')
    qs = Comunidad.objects.filter(estado=Comunidad.Estado.ACTIVA).annotate(
        n_integrantes=Count('membresias', distinct=True), n_eventos=Count('eventos', distinct=True))
    if tipo in Comunidad.Tipo.values:
        qs = qs.filter(tipo=tipo)
    if cat in Comunidad.Categoria.values:
        qs = qs.filter(categoria=cat)
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q) | Q(lugar__icontains=q))
    total = Comunidad.objects.filter(estado=Comunidad.Estado.ACTIVA).count()
    return render(request, 'comunidades/lista.html', {
        'comunidades': qs, 'q': q, 'tipo': tipo, 'cat': cat, 'total': total,
        'tipos': [('todas', 'Todas'), ('oficial', 'GG.OO. reconocidos'), ('emergente', 'Emergentes')],
        'categorias': Comunidad.Categoria.choices,
    })


def detalle(request, slug):
    """Ficha de la comunidad (P-16) con eventos, foro (P-33) e integrantes."""
    c = get_object_or_404(Comunidad, slug=slug)
    es_coord = c.es_coordinador(request.user)
    if c.estado != Comunidad.Estado.ACTIVA and not (es_coord or request.user.is_staff):
        raise PermissionDenied
    tab = request.GET.get('tab', 'eventos')
    membresias = c.membresias.select_related('usuario')
    ver_integrantes = c.integrantes_publicos or es_coord or request.user.is_staff
    return render(request, 'comunidades/detalle.html', {
        'c': c, 'tab': tab, 'es_coord': es_coord, 'es_integrante': c.es_integrante(request.user),
        'eventos': eventos_con_cupos(request.user).filter(comunidad=c),
        'mensajes': c.mensajes_foro.select_related('autor'),
        'coordinadores_ids': {m.usuario_id for m in membresias if m.rol == Membresia.Rol.COORDINADOR},
        'membresias': membresias[:12], 'n_integrantes': membresias.count(),
        'ver_integrantes': ver_integrantes,
        'form': MensajeForm(), 'motivos': Reporte.Motivo.choices,
    })


@login_required
def nueva(request):
    """Registro de comunidad (P-32). Queda pendiente hasta que administración la revise."""
    form = ComunidadForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        c = form.save(commit=False)
        c.creada_por = request.user
        c.estado = Comunidad.Estado.PENDIENTE
        c.activa_desde = 'oct. 2026'
        c.save()
        Membresia.objects.create(usuario=request.user, comunidad=c, rol=Membresia.Rol.COORDINADOR)
        staff = get_user_model().objects.filter(is_staff=True)
        notificar(staff, Notificacion.Tipo.SOLICITUD, f'Solicitud de nueva comunidad: {c.nombre}',
                  f'{request.user.get_full_name()} quiere registrar “{c.nombre}”.', '/moderacion/')
        messages.success(request, 'Solicitud enviada. Te avisaremos cuando la comunidad esté publicada.')
        return redirect('comunidades:lista')
    return render(request, 'comunidades/form.html', {'form': form, 'editando': False})


@login_required
def editar(request, slug):
    c = get_object_or_404(Comunidad, slug=slug)
    if not c.es_coordinador(request.user):
        raise PermissionDenied
    form = ComunidadForm(request.POST or None, instance=c)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ficha actualizada')
        return redirect(c)
    return render(request, 'comunidades/form.html', {'form': form, 'editando': True, 'c': c})


@login_required
@require_POST
def unirse(request, slug):
    c = get_object_or_404(Comunidad, slug=slug, estado=Comunidad.Estado.ACTIVA)
    _, creada = Membresia.objects.get_or_create(usuario=request.user, comunidad=c)
    if creada:
        notificar(c.coordinadores(), Notificacion.Tipo.SOLICITUD, f'Nuevo integrante en {c.nombre}',
                  f'{request.user.get_full_name()} se unió a la comunidad.', c.get_absolute_url() + '?tab=integrantes')
        messages.success(request, 'Te uniste. Ahora recibirás los avisos de esta comunidad.')
    return redirect(c)


@login_required
@require_POST
def salir(request, slug):
    c = get_object_or_404(Comunidad, slug=slug)
    Membresia.objects.filter(usuario=request.user, comunidad=c, rol=Membresia.Rol.INTEGRANTE).delete()
    messages.success(request, f'Saliste de {c.nombre}')
    return redirect(c)


@login_required
@require_POST
def publicar_foro(request, slug):
    c = get_object_or_404(Comunidad, slug=slug, estado=Comunidad.Estado.ACTIVA)
    form = MensajeForm(request.POST)
    if form.is_valid():
        m = form.save(commit=False)
        m.autor, m.comunidad = request.user, c
        m.save()
        destinatarios = [mb.usuario for mb in c.membresias.select_related('usuario').exclude(usuario=request.user)]
        notificar(destinatarios, Notificacion.Tipo.MENSAJE, f'Nuevo mensaje en {c.nombre}',
                  f'{request.user.get_full_name()}: “{m.texto[:120]}”', m.get_absolute_url())
        messages.success(request, 'Mensaje publicado en el foro')
    return redirect(f'{c.get_absolute_url()}?tab=foro')
