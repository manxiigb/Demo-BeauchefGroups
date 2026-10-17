"""Utilidades compartidas de formularios."""

def estilizar(form):
    """Agrega la clase .inp del diseño a los campos de texto, número, fecha y select."""
    from django import forms as f
    for campo in form.fields.values():
        if not isinstance(campo.widget, (f.RadioSelect, f.CheckboxInput, f.HiddenInput)):
            campo.widget.attrs['class'] = (campo.widget.attrs.get('class', '') + ' inp').strip()
