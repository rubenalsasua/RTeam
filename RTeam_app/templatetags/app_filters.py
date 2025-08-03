from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def dictsortby(value, arg):
    """Sort a list of dictionaries by key"""
    return sorted(value, key=lambda d: d.get(arg, ''))
