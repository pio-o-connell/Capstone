from django import template

register = template.Library()


@register.filter
def get_price(service, size):
    """Get price for a service based on size."""
    if service is None:
        return 0
    return service.get_price(size)
