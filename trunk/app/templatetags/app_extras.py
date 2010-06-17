from django import template
register = template.Library()

@register.filter(name='display')

def display(value):
    if value == 1:
        return 'Pendiente'
    elif value == 2:
        return 'Modificado'
    elif value == 3:
        return 'Revisado'
    return ''
