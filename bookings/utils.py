# bookings/utils.py
from .models import CartItem


def migrate_guest_cart_to_user(request, user):
    """Attach any guest cart rows for the current session to the authenticated user."""
    session_key = request.session.session_key
    if not session_key:
        return

    guest_items = CartItem.objects.filter(session_id=session_key, user__isnull=True)
    for item in guest_items:
        # Try to merge with existing user item (same service, size, date)
        existing, created = CartItem.objects.get_or_create(
            user=user,
            service=item.service,
            size=item.size,
            date=item.date,
            defaults={"quantity": 0}
        )
        existing.quantity += item.quantity
        existing.save()
        item.delete()
