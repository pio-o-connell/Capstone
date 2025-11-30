# users/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from bookings.utils import migrate_guest_cart_to_user

@receiver(user_logged_in)
def migrate_cart_on_login(sender, request, user, **kwargs):
    migrate_guest_cart_to_user(request, user)
