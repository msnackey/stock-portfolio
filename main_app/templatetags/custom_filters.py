from django import template
import locale

register = template.Library()

@register.filter(name='dict_key')
def dict_key(dict, key):
    '''Returns the given key from a dictionary.'''
    return dict[key]

@register.filter(name='num')
def num(value, decimals):
    if decimals == "0":
        return locale.format_string('%.f', value, grouping=True)
    elif decimals == "1":
        return locale.format_string('%.1f', value, grouping=True)
    elif decimals == "2":
        return locale.format_string('%.2f', value, grouping=True)
    elif decimals == "3":
        return locale.format_string('%.3f', value, grouping=True)
    else:
        raise

@register.filter(name='cur')
def cur(value, decimals):
    if decimals == "0":
        return locale.format_string('%.f', value, grouping=True, monetary=True)
    elif decimals == "1":
        return locale.format_string('%.1f', value, grouping=True, monetary=True)
    elif decimals == "2":
        return locale.format_string('%.2f', value, grouping=True, monetary=True)
    elif decimals == "3":
        return locale.format_string('%.3f', value, grouping=True, monetary=True)
    else:
        raise