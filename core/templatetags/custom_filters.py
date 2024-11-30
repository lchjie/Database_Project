from django import template

register = template.Library()

@register.filter
def sum_prices(items):
    return sum(item.price for item in items)

