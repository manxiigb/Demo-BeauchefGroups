import datetime

from django import forms
from django.utils import timezone

from core.forms import estilizar

from .models import Evento, Mensaje


class EventoForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora_inicio = forms.TimeField(label='Inicio', widget=forms.TimeInput(attrs={'type': 'time'}))
    hora_fin = forms.TimeField(label='Término', widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Evento
        fields = ['comunidad', 'titulo', 'modalidad', 'lugar', 'cupos', 'descripcion',
                  'lista_espera', 'pedir_confirmacion']
        widgets = {
            'modalidad': forms.RadioSelect,
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'cupos': forms.NumberInput(attrs={'min': 1, 'max': 500}),
        }
        help_texts = {'cupos': 'Cuando se llenen, las siguientes personas quedan en lista de espera.'}

    def __init__(self, *args, comunidades=None, **kwargs):
        super().__init__(*args, **kwargs)
        if comunidades is not None:
            self.fields['comunidad'].queryset = comunidades
            if comunidades.count() == 1:
                self.fields['comunidad'].initial = comunidades.first()
                self.fields['comunidad'].widget = forms.HiddenInput()
        self.fields['fecha'].widget.attrs['min'] = timezone.localdate().isoformat()
        estilizar(self)

    def clean(self):
        data = super().clean()
        f, hi, hf = data.get('fecha'), data.get('hora_inicio'), data.get('hora_fin')
        if f and hi and hf:
            tz = timezone.get_current_timezone()
            inicio = timezone.make_aware(datetime.datetime.combine(f, hi), tz)
            fin = timezone.make_aware(datetime.datetime.combine(f, hf), tz)
            if fin <= inicio:
                self.add_error('hora_fin', 'El término debe ser después del inicio.')
            if inicio < timezone.now():
                self.add_error('fecha', 'Elige una fecha y hora que aún no hayan pasado.')
            data['inicio'], data['fin'] = inicio, fin
        return data

    def save(self, commit=True):
        self.instance.inicio = self.cleaned_data['inicio']
        self.instance.fin = self.cleaned_data['fin']
        return super().save(commit)


class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['texto']
        widgets = {'texto': forms.TextInput(attrs={'placeholder': 'Pregunta algo a la organización',
                                                   'aria-label': 'Mensaje', 'maxlength': 1000})}
