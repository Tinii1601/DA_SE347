from django import template

register = template.Library()

@register.filter
def vnd_currency(value):
    """
    Converts a number to a Vietnamese currency string.
    Example: 49000 -> 49.000đ
    """
    try:
        value = float(value)
        return "{:,.0f}".format(value).replace(",", ".") + "đ"
    except (ValueError, TypeError):
        return value
