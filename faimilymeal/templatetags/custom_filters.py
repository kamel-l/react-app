from django import template
from django import template
from itertools import groupby
from operator import itemgetter

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retourne la valeur pour la clé donnée d'un dictionnaire."""
    return dictionary.get(key)


register = template.Library()

@register.filter
def format_quantity(value):
    try:
        num = float(value)
        if num.is_integer():
            return int(num)
        return '{:.1f}'.format(num)
    except:
        return value


@register.filter
def groupby(value, key):
    """
    Group a list of dictionaries by a specified key.
    """
    try:
        if not isinstance(value, list):
            raise ValueError("Input must be a list of dictionaries.")

        sorted_value = sorted(value, key=itemgetter(key))
        grouped = groupby(sorted_value, key=itemgetter(key))
        return {k: list(v) for k, v in grouped}
    except Exception as e:
        # Retourne une liste vide ou une autre valeur par défaut en cas d'erreur
        return []
    
    
CATEGORY_NAMES = {
    'fruits_legumes': 'Fruits et Légumes',
    'viandes_poissons': 'Viandes et Poissons',
    'produits_laitiers': 'Produits Laitiers',
    'epicerie': 'Épicerie',
    'boissons': 'Boissons',
    'autres': 'Autres',
}

@register.filter
def category_name(value):
    """Convert category keys to human-readable names."""
    return CATEGORY_NAMES.get(value, value)

MEAL_TYPE_NAMES = {
    'breakfast': 'Petit-déjeuner',
    'lunch': 'Déjeuner',
    'dinner': 'Dîner',
}

@register.filter
def meal_type_name(value):
    """Convert meal type keys to human-readable names."""
    return MEAL_TYPE_NAMES.get(value, value)    