from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CartItem, Booking
from django.utils import timezone

# Guest: Add to session cart
def add_to_cart_guest(request):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        cart.append({
            'service_name': request.POST['service_name'],
            'date': request.POST['date'],
        })
        request.session['cart'] = cart
        return redirect('view_cart_guest')
    return render(request, 'bookings/add_guest.html')

def view_cart_guest(request):
    cart = request.session.get('cart', [])
    return render(request, 'bookings/guest_cart.html', {'cart': cart})

def confirm_guest_booking(request):
    cart = request.session.get('cart', [])
    for item in cart:
        Booking.objects.create(
            user=None,
            service_name=item['service_name'],
            date=item['date'],
            status='pending'
        )
    request.session['cart'] = []
    return redirect('view_cart_guest')

# Registered users
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        CartItem.objects.create(
            user=request.user,
            service_name=request.POST['service_name'],
            date=request.POST['date']
        )
        return redirect('view_cart')
    return render(request, 'bookings/add_cart.html')

@login_required
def view_cart(request):
    cart = CartItem.objects.filter(user=request.user)
    return render(request, 'bookings/cart.html', {'cart': cart})

@login_required
def confirm_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        Booking.objects.create(
            user=request.user,
            service_name=item.service_name,
            date=item.date,
            status='pending'
        )
    cart_items.delete()
    return redirect('view_cart')


def booking_home(request):
    """Render the bookings home page."""
    return render(request, 'booking/booking_home.html')


def services_home(request):
    """Render a copy of the services landing page inside bookings."""
    return render(request, 'booking/services_home.html')

