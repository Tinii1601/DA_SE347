from django import template

register = template.Library()

@register.filter
def vnd_currency(value):
    """
    Converts a number to a Vietnamese currency string.
    Example: 49000 -> 49.000 VNĐ
    """
    try:
        value = int(value)
        return "{:,.0f}".format(value).replace(",", ".") + " VNĐ"
    except (ValueError, TypeError):
        return value
