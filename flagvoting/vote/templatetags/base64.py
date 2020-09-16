from base64 import b64encode

from django import template

register = template.Library()


@register.filter
def base64(value):
    return b64encode(value.encode()).decode("UTF-8")
