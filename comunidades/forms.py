from django import forms

from core.forms import estilizar

from .models import Comunidad


class ComunidadForm(forms.ModelForm):
    class Meta:
        model = Comunidad
        fields = ['nombre', 'tipo', 'categoria', 'lugar', 'descripcion', 'integrantes_publicos']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej.: Club de Astronomía Beauchef'}),
            'tipo': forms.RadioSelect,
            'lugar': forms.TextInput(attrs={'placeholder': 'Sala, patio o en línea'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Cuenta en dos o tres frases qué hace el grupo y a quién buscan.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['integrantes_publicos'] = forms.TypedChoiceField(
            label='¿Quién puede ver la lista de integrantes?',
            choices=[(True, 'Cualquier estudiante'), (False, 'Solo coordinación')],
            coerce=lambda v: v in (True, 'True', 'true', '1'),
            widget=forms.RadioSelect, initial=True)
        estilizar(self)
