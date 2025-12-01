
# users/signals.py
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.utils import migrate_guest_cart_to_user
from .models import CustomUser, CustomerProfile, BloggerProfile, BloggerRequest

@receiver(user_logged_in)
def migrate_cart_on_login(sender, request, user, **kwargs):
    migrate_guest_cart_to_user(request, user)

@receiver(post_save, sender=CustomUser)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user=instance)


@receiver(post_save, sender=BloggerRequest)
def create_blogger_profile_on_approval(sender, instance, created, **kwargs):
    if not created and instance.approved:
        user = instance.user
        if not user.is_blogger:
            user.become_blogger()  # Sets group + flag
        BloggerProfile.objects.get_or_create(user=user)