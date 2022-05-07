from django import template

register = template.Library()

@register.simple_tag
def myconcat(value1, value2):
    return value1 + value2