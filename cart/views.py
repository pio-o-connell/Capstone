from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from bookings.models import Booking
from .models import CartItem



# Registered user adds to cart
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        CartItem.objects.create(
            user=request.user,
            service_name=request.POST['service_name'],
            date=request.POST['date']
        )
        return redirect('view_cart')

# View registered user's cart
@login_required
def view_cart(request):
    cart = CartItem.objects.filter(user=request.user)
    return render(request, 'bookings/cart.html', {'cart': cart})

# Confirm cart → create Bookings
@login_required
def confirm_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        Booking.objects.create(
            user=request.user,
            service_name=item.service_name,
            date=item.date,
            approved=False
        )
    cart_items.delete()
    return redirect('booking_pending')





@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        Booking.objects.create(
            user=request.user,
            service_name=item.service_name,
            date=item.date,
            quantity=item.quantity
        )

    # Clear cart after checkout
    cart_items.delete()

    return redirect('booking_confirmation')

# Create your views here.
@login_required
def migrate_guest_cart_to_user(request):
    guest_cart = request.session.get('guest_cart', [])
    for item in guest_cart:
        CartItem.objects.create(
            user=request.user,
            service_name=item['service_name'],
            date=item['date']
        )
    if 'guest_cart' in request.session:
        del request.session['guest_cart']
        request.session.modified = True
    return redirect('view_cart')
