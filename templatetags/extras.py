from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(str(key))
    except:
        return None

@register.filter
def get_item_int(dictionary, key):
    return dictionary.get(key)

@register.filter
def return_item(l, i):
    try:
        return l[i]
    except:
        return None

@register.simple_tag
def define_int(val=None):
    try:
        return int(val)
    except:
        return None

@register.simple_tag
def define(val=None):
    try:
        return val
    except:
        return None

@register.simple_tag
def list_to_string(val=None):
    try:
        return str(val)[1:-1]
    except:
        return None
