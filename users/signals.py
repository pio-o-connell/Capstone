
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from bookings.utils import migrate_guest_cart_to_user
from .models import (
    BloggerProfile,
    BloggerRequest,
    CustomUser,
    CustomerProfile,
    UserNotification,
)


# 1. Migrate guest cart to user on login
@receiver(user_logged_in)
def migrate_cart_on_login(sender, request, user, **kwargs):
    migrate_guest_cart_to_user(request, user)


# 1b. Surface queued notifications when the user logs in
@receiver(user_logged_in)
def deliver_login_notifications(sender, request, user, **kwargs):
    pending = UserNotification.objects.filter(user=user, delivered=False)
    for note in pending:
        messages.info(request, note.message)
    pending.update(delivered=True)


# 2. Auto-create CustomerProfile on user registration
@receiver(post_save, sender=CustomUser)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user=instance)


# 3. Create BloggerProfile when BloggerRequest is approved
@receiver(post_save, sender=BloggerRequest)
def create_blogger_profile_on_approval(sender, instance, created, **kwargs):
    if not created and instance.approved:
        user = instance.user
        if not user.is_blogger:
            user.become_blogger()
        BloggerProfile.objects.get_or_create(user=user)
