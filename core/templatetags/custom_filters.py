from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtener un elemento de un diccionario por clave"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def get_completed(dictionary, key):
    """Obtener el estado 'completed' de un elemento en un diccionario"""
    if dictionary is None:
        return False
    item = dictionary.get(key)
    if item is None:
        return False
    return item.get('completed', False) if isinstance(item, dict) else bool(item)

@register.filter
def get_score(dictionary, key):
    """Obtener la puntuación de un elemento en un diccionario"""
    if dictionary is None:
        return 0
    item = dictionary.get(key)
    if item is None:
        return 0
    return item.get('score', 0) if isinstance(item, dict) else 0
