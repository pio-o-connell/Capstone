# bookings/utils.py
from .models import CartItem

def migrate_guest_cart_to_user(request, user):
    """
    Moves guest session cart to the registered user's CartItem table.
    Call this right after login or registration.
    """
    session_cart = request.session.get('cart', [])
    for item in session_cart:
        CartItem.objects.create(
            user=user,
            service_name=item['service_name'],
            date=item['date']
        )
    # Clear the session cart
    request.session['cart'] = []
