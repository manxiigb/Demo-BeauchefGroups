from .models import Notificacion


def notificar(usuarios, tipo, titulo, texto='', url=''):
    """Crea una notificación para cada usuario. En producción también enviaría push/correo (P-36)."""
    if not hasattr(usuarios, '__iter__'):
        usuarios = [usuarios]
    Notificacion.objects.bulk_create([
        Notificacion(usuario=u, tipo=tipo, titulo=titulo[:140], texto=texto[:300], url=url)
        for u in {u.pk: u for u in usuarios}.values()
    ])
