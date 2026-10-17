from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Comunidad(models.Model):
    """GG.OO. reconocido o grupo emergente (P-32, P-34, P-27)."""

    class Tipo(models.TextChoices):
        OFICIAL = 'oficial', 'GG.OO. reconocido'
        EMERGENTE = 'emergente', 'Grupo emergente'

    class Categoria(models.TextChoices):
        DEPORTE = 'deporte', 'Deporte'
        ARTE = 'arte', 'Arte y música'
        TECNOLOGIA = 'tecnologia', 'Tecnología'
        JUEGOS = 'juegos', 'Juegos y estrategia'
        AMBIENTE = 'ambiente', 'Medio ambiente'
        VOLUNTARIADO = 'voluntariado', 'Voluntariado'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente de revisión'
        ACTIVA = 'activa', 'Activa'
        OBSERVADA = 'observada', 'Necesita más información'

    nombre = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.EMERGENTE)
    categoria = models.CharField(max_length=15, choices=Categoria.choices)
    descripcion = models.TextField('¿Qué hacen?')
    lugar = models.CharField('Dónde se reúnen', max_length=120, blank=True)
    activa_desde = models.CharField(max_length=20, blank=True, help_text='Ej.: 2011 o sep. 2026')
    integrantes_publicos = models.BooleanField(
        'Cualquier estudiante puede ver la lista de integrantes', default=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    creada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='comunidades_creadas')
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'comunidades'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nombre)[:60] or 'comunidad'
            slug, n = base, 2
            while Comunidad.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f'{base}-{n}', n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('comunidades:detalle', args=[self.slug])

    @property
    def iniciales(self):
        palabras = [p for p in self.nombre.split() if p[0].isalnum()]
        return ''.join(p[0] for p in palabras[:2]).upper()

    @property
    def es_emergente(self):
        return self.tipo == self.Tipo.EMERGENTE

    def coordinadores(self):
        return [m.usuario for m in self.membresias.filter(rol=Membresia.Rol.COORDINADOR).select_related('usuario')]

    def es_coordinador(self, user):
        return user.is_authenticated and self.membresias.filter(
            usuario=user, rol=Membresia.Rol.COORDINADOR).exists()

    def es_integrante(self, user):
        return user.is_authenticated and self.membresias.filter(usuario=user).exists()


class Membresia(models.Model):
    class Rol(models.TextChoices):
        COORDINADOR = 'coordinador', 'Coordinación'
        INTEGRANTE = 'integrante', 'Integrante'

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membresias')
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='membresias')
    rol = models.CharField(max_length=12, choices=Rol.choices, default=Rol.INTEGRANTE)
    desde = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('usuario', 'comunidad')]
        ordering = ['rol', 'desde']

    def __str__(self):
        return f'{self.usuario} en {self.comunidad} ({self.get_rol_display()})'
