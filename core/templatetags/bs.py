from django import template
from django.forms import CheckboxInput, CheckboxSelectMultiple, Select, SelectMultiple
from django.utils.html import format_html, format_html_join

register = template.Library()


@register.filter
def bs(field):
    """Renderiza o campo com a classe Bootstrap adequada ao widget."""
    widget = field.field.widget
    if isinstance(widget, CheckboxSelectMultiple):
        # O Django poria a classe na <div> que envolve as opções; montamos cada opção no padrão .form-check.
        for opcao in field.subwidgets:
            opcao.data['attrs']['class'] = 'form-check-input'
        return format_html_join(
            '', '<div class="form-check form-check-inline">{}<label class="form-check-label" for="{}">{}</label></div>',
            ((opcao.tag(), opcao.id_for_label, opcao.choice_label) for opcao in field.subwidgets),
        )
    if isinstance(widget, CheckboxInput):
        css = 'form-check-input'
    elif isinstance(widget, (Select, SelectMultiple)):
        css = 'form-select'
    else:
        css = 'form-control'
    if field.errors:
        css += ' is-invalid'
    return field.as_widget(attrs={'class': css})
