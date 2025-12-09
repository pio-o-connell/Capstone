# # from django.shortcuts import render, redirect
# # from django.contrib.auth.decorators import login_required
# # from .models import CartItem, Booking
# # from django.utils import timezone

# # # Guest: Add to session cart
# # def add_to_cart_guest(request):
# #     if request.method == 'POST':
# #         cart = request.session.get('cart', [])
# #         cart.append({
# #             'service_name': request.POST['service_name'],
# #             'date': request.POST['date'],
# #         })
# #         request.session['cart'] = cart
# #         return redirect('view_cart_guest')
# #     # No dedicated add_guest template exists; redirect guests to the bookings services page
# #     return redirect('booking_services')

# # def view_cart_guest(request):
# #     cart = request.session.get('cart', [])
# #     # Template is located under bookings/templates/booking/guest_cart.html
# #     return render(request, 'booking/guest_cart.html', {'cart': cart})

# # def confirm_guest_booking(request):
# #     cart = request.session.get('cart', [])
# #     for item in cart:
# #         Booking.objects.create(
# #             user=None,
# #             service_name=item['service_name'],
# #             date=item['date'],
# #             status='pending'
# #         )
# #     request.session['cart'] = []
# #     return redirect('view_cart_guest')

# # # Registered users
# # @login_required
# # def add_to_cart(request):
# #     if request.method == 'POST':
# #         CartItem.objects.create(
# #             user=request.user,
# #             service_name=request.POST['service_name'],
# #             date=request.POST['date']
# #         )
# #         return redirect('view_cart')
# #     # No dedicated add_cart template; redirect to services landing inside bookings
# #     return redirect('booking_services')

# # @login_required
# # def view_cart(request):
# #     cart = CartItem.objects.filter(user=request.user)
# #     # Template files live under bookings/templates/booking/, so render that path
# #     return render(request, 'booking/cart.html', {'cart': cart})

# # @login_required
# # def confirm_cart(request):
# #     cart_items = CartItem.objects.filter(user=request.user)
# #     for item in cart_items:
# #         Booking.objects.create(
# #             user=request.user,
# #             service_name=item.service_name,
# #             date=item.date,
# #             status='pending'
# #         )
# #     cart_items.delete()
# #     return redirect('view_cart')


# # def booking_home(request):
# #     """Render the bookings home page."""
# #     return render(request, 'booking/booking_home.html')


# # def services_home(request):
# #     """Render a copy of the services landing page inside bookings."""
# #     return render(request, 'booking/services_home.html')

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from .models import CartItem, Booking
# from services.models import Service  # <- import Service
# from django.http import JsonResponse
# import json


# def add_to_cart_guest(request):
#     if request.method == 'POST':
#         service_id = request.POST.get('service_id')
#         size = request.POST.get('size', 'small')
#         quantity = int(request.POST.get('quantity', 1))
#         date = request.POST.get('date')

#         service = get_object_or_404(Service, id=service_id)

#         cart = request.session.get('cart', [])
#         cart.append({
#             'service_id': service.id,
#             'service_name': service.name,
#             'size': size,
#             'quantity': quantity,
#             'date': date,
#             'price': float(service.get_price(size))
#         })
#         request.session['cart'] = cart
#         return redirect('view_cart_guest')

#     return redirect('services_home')  # redirect guests to services page

# def view_cart_guest(request):
#     cart = request.session.get('cart', [])
#     total = sum(item['price'] * item['quantity'] for item in cart)
#     return render(request, 'booking/guest_cart.html', {'cart': cart, 'total': total})

# def confirm_guest_booking(request):
#     cart = request.session.get('cart', [])
#     for item in cart:
#         Booking.objects.create(
#             user=None,
#             service_id=item['service_id'],
#             size=item['size'],
#             quantity=item['quantity'],
#             date=item['date'],
#             status='pending'
#         )
#     request.session['cart'] = []
#     return redirect('view_cart_guest')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CartItem, Booking
from services.models import Service
import json


# Landing page
def booking_home(request):
    """Render the bookings landing page."""
    return render(request, 'booking/booking_home.html')

# Guest Cart
def add_to_cart_guest(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        size = request.POST.get('size', 'small')
        quantity = int(request.POST.get('quantity', 1))
        date = request.POST.get('date')
        service = get_object_or_404(Service, id=service_id)

        cart = request.session.get('cart', [])
        cart.append({
            'service_id': service.id,
            'service_name': service.name,
            'size': size,
            'quantity': quantity,
            'date': date,
            'price': float(service.get_price(size))
        })
        request.session['cart'] = cart
        return redirect('view_cart_guest')
    return redirect('services:services_home')

def view_cart_guest(request):
    cart = request.session.get('cart', [])
    total = sum(item['price']*item['quantity'] for item in cart)
    return render(request, 'booking/guest_cart.html', {'cart': cart, 'total': total})

def confirm_guest_booking(request):
    cart = request.session.get('cart', [])
    for item in cart:
        Booking.objects.create(
            user=None,
            service_id=item['service_id'],
            size=item['size'],
            quantity=item['quantity'],
            date=item['date'],
            status='pending'
        )
    request.session['cart'] = []
    return redirect('view_cart_guest')


# Registered Users
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        size = request.POST.get('size', 'small')
        quantity = int(request.POST.get('quantity', 1))
        date = request.POST.get('date')
        service = get_object_or_404(Service, id=service_id)

        CartItem.objects.create(
            user=request.user,
            service=service,
            size=size,
            quantity=quantity,
            date=date
        )
        return redirect('view_cart')
    return redirect('services:services_home')

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'booking/cart.html', {'cart': cart_items, 'total': total})

@login_required
def confirm_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        Booking.objects.create(
            user=request.user,
            service=item.service,
            size=item.size,
            quantity=item.quantity,
            date=item.date,
            status='pending'
        )
    cart_items.delete()
    return redirect('view_cart')


# AJAX Add-to-Cart for logged-in users
@login_required
def add_to_cart_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        service_id = data.get("service_id")
        size = data.get("size", "small")
        quantity = int(data.get("quantity", 1))
        service = get_object_or_404(Service, id=service_id)

        CartItem.objects.create(
            user=request.user,
            service=service,
            size=size,
            quantity=quantity
        )
        return JsonResponse({"message": f"{service.name} ({size}) added to cart!"})
    return JsonResponse({"error": "Invalid request"}, status=400)


@require_GET
def cart_summary(request):
    """Return a lightweight JSON summary of the current cart."""
    items = []
    total = 0

    if request.user.is_authenticated:
        cart_items = (
            CartItem.objects.filter(user=request.user)
            .select_related("service")
            .order_by("-added_at")
        )
        for item in cart_items:
            service = item.service
            price = service.get_price(item.size) if service else 0
            subtotal = float(price or 0) * item.quantity
            total += subtotal
            items.append({
                "id": item.id,
                "service": service.name if service else "Service unavailable",
                "size": item.get_size_display(),
                "quantity": item.quantity,
                "price": float(price or 0),
                "subtotal": round(subtotal, 2),
                "image": service.image.url if service and service.image else None,
            })
    else:
        session_cart = request.session.get("cart", [])
        service_ids = {entry.get("service_id") for entry in session_cart if entry.get("service_id")}
        service_lookup = {
            svc.id: svc for svc in Service.objects.filter(id__in=service_ids)
        }

        for idx, entry in enumerate(session_cart):
            service = service_lookup.get(entry.get("service_id"))
            price = entry.get("price")
            if price is None and service:
                price = float(service.get_price(entry.get("size")) or 0)
            subtotal = float(price or 0) * entry.get("quantity", 1)
            total += subtotal
            items.append({
                "id": idx,
                "service": entry.get("service_name") or (service.name if service else "Service"),
                "size": entry.get("size", "small").title(),
                "quantity": entry.get("quantity", 1),
                "price": float(price or 0),
                "subtotal": round(subtotal, 2),
                "image": service.image.url if service and service.image else None,
            })

    return JsonResponse({
        "items": items,
        "total": round(total, 2),
        "count": len(items),
    })


