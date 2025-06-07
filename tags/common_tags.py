from django import template

register = template.Library()


@register.filter(name='hash')
def hash(h, key):
    return h[key]

@register.filter(name='value_from_object')
def value_from_object(object, field):
    return getattr(object, field, '')

@register.filter(name='dict')
def dict(h):
    return h.keys()


@register.filter(name='verbose_name')
def verbose_name(obj):
    return obj._meta.verbose_name

@register.filter(name='verbose_name_plural')
def verbose_name(obj):
    return obj._meta.verbose_name_plural

@register.filter(name='app_name')
def app_name(obj):
    return obj._meta.app_label

@register.filter(name='colsize')
def colsize(d):
    return str(12//len(d))
