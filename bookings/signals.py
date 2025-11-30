# bookings/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import CartItem

@receiver(user_logged_in)
def migrate_cart_on_login(sender, request, user, **kwargs):
    guest_cart = request.session.get('guest_cart', [])
    for item in guest_cart:
        CartItem.objects.create(
            user=user,
            service_name=item['service_name'],
            date=item['date']
        )
    if 'guest_cart' in request.session:
        del request.session['guest_cart']
        request.session.modified = True
