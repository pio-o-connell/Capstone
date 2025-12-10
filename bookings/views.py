from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import CartItem, Booking
from services.models import Service
import json


def _ensure_session_key(request):
    """Guarantee that the current request has a session key."""
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def _cart_queryset(request):
    if request.user.is_authenticated:
        return (
            CartItem.objects.filter(user=request.user)
            .select_related("service")
            .order_by("-added_at")
        )
    session_key = request.session.session_key
    if not session_key:
        return CartItem.objects.none()
    return (
        CartItem.objects.filter(session_id=session_key, user__isnull=True)
        .select_related("service")
        .order_by("-added_at")
    )


def _parse_date(date_value):
    if not date_value:
        return None
    try:
        return datetime.strptime(date_value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _add_item_to_cart(request, service, size, quantity, date_value=None):
    if quantity <= 0:
        return None

    size = (size or "small").lower()
    parsed_date = _parse_date(date_value)

    lookup = {
        "service": service,
        "size": size,
        "date": parsed_date,
    }

    if request.user.is_authenticated:
        lookup["user"] = request.user
        lookup["session_id"] = None
    else:
        lookup["user"] = None
        lookup["session_id"] = _ensure_session_key(request)

    cart_item, _ = CartItem.objects.get_or_create(defaults={"quantity": 0}, **lookup)
    cart_item.quantity += quantity
    cart_item.save()
    return cart_item


def _finalize_cart_items(cart_items, user=None):
    """Persist bookings for every cart item and then clear the cart."""
    bookings_created = []
    today = timezone.now().date()

    for item in cart_items:
        booking = Booking.objects.create(
            user=user,
            service=item.service,
            size=item.size,
            quantity=item.quantity,
            date=item.date or today,
            status='pending'
        )
        bookings_created.append(booking)

    cart_items.delete()
    return bookings_created


def _serialize_cart(cart_items):
    items = []
    total = 0

    for item in cart_items:
        service = item.service
        price = service.get_price(item.size) if service else 0
        price_value = float(price or 0)
        subtotal = round(price_value * item.quantity, 2)
        total += subtotal
        size_label = (
            item.get_size_display()
            if hasattr(item, "get_size_display")
            else item.size.title()
        )
        image_url = None
        if service and getattr(service, "image", None):
            image_url = service.image.url

        items.append(
            {
                "id": item.id,
                "service": service.name if service else "Service unavailable",
                "size": size_label,
                "quantity": item.quantity,
                "price": round(price_value, 2),
                "subtotal": subtotal,
                "image": image_url,
            }
        )

    return {
        "items": items,
        "total": round(total, 2),
        "count": len(items),
    }


def _resolve_service(service_id=None, service_name=None):
    """Resolve a Service by id or name (case-insensitive)."""
    if service_id:
        try:
            return Service.objects.get(id=service_id)
        except Service.DoesNotExist as exc:
            raise Http404("Requested service was not found") from exc

    if service_name:
        service = Service.objects.filter(name__iexact=service_name.strip()).first()
        if service:
            return service
        raise Http404("Requested service was not found")

    raise Http404("Service identifier missing")


# Landing page
def booking_home(request):
    """Render the bookings landing page."""
    return render(request, 'booking/booking_home.html')


def add_to_cart_guest(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id') or request.POST.get('service')
        service_name = request.POST.get('service_name')
        size = request.POST.get('size', 'small')
        quantity = request.POST.get('quantity', 1)
        date = request.POST.get('date')

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 1

        service = _resolve_service(service_id, service_name)
        _add_item_to_cart(request, service, size, quantity, date)
        return redirect('view_cart_guest')
    return redirect('services:services_home')


def view_cart_guest(request):
    session_key = request.session.session_key
    if not session_key:
        cart_items = CartItem.objects.none()
    else:
        cart_items = (
            CartItem.objects.filter(
                session_id=session_key,
                user__isnull=True,
            )
            .select_related('service')
        )
    total = sum(item.total_price() for item in cart_items)
    return render(
        request,
        'booking/guest_cart.html',
        {
            'cart': cart_items,
            'total': total,
        },
    )


def confirm_guest_booking(request):
    if request.method != 'POST':
        return redirect('view_cart_guest')

    session_key = request.session.session_key
    if not session_key:
        return redirect('view_cart_guest')

    cart_items = (
        CartItem.objects.filter(
            session_id=session_key,
            user__isnull=True,
        )
        .select_related('service')
    )
    if not cart_items.exists():
        return render(
            request,
            'booking/booking_confirmation.html',
            {
                'bookings': [],
                'booking_count': 0,
                'is_guest': True,
            },
        )

    bookings_created = _finalize_cart_items(cart_items, user=None)
    return render(
        request,
        'booking/booking_confirmation.html',
        {
            'bookings': bookings_created,
            'booking_count': len(bookings_created),
            'is_guest': True,
        },
    )


# Registered Users
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id') or request.POST.get('service')
        service_name = request.POST.get('service_name')
        size = request.POST.get('size', 'small')
        quantity = request.POST.get('quantity', 1)
        date = request.POST.get('date')

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 1

        service = _resolve_service(service_id, service_name)
        _add_item_to_cart(request, service, size, quantity, date)
        return redirect('view_cart')
    return redirect('services:services_home')


@login_required
def view_cart(request):
    cart_items = _cart_queryset(request)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'booking/cart.html', {'cart': cart_items, 'total': total})


@login_required
def confirm_cart(request):
    cart_items = _cart_queryset(request)
    if not cart_items.exists():
        return render(request, 'booking/booking_confirmation.html', {
            'bookings': [],
            'booking_count': 0,
            'is_guest': False,
        })

    bookings_created = _finalize_cart_items(cart_items, user=request.user)
    return render(request, 'booking/booking_confirmation.html', {
        'bookings': bookings_created,
        'booking_count': len(bookings_created),
        'is_guest': False,
    })


@require_POST
def add_to_cart_ajax(request):
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    raw_items = payload.get("items")
    if isinstance(raw_items, dict):
        raw_items = [raw_items]
    if not raw_items:
        has_service = payload.get("service_id") or payload.get("service_name")
        raw_items = [payload] if has_service else []

    added = 0
    for entry in raw_items:
        if not isinstance(entry, dict):
            continue
        quantity = entry.get("quantity", 0)
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 0

        if quantity <= 0:
            continue

        service_id = entry.get("service_id")
        service_name = entry.get("service_name") or entry.get("service")
        size = entry.get("size", "small")
        date = entry.get("date")

        try:
            service = _resolve_service(service_id, service_name)
        except Http404:
            continue

        created_item = _add_item_to_cart(request, service, size, quantity, date)
        if created_item:
            added += 1

    if not added:
        return JsonResponse({"error": "No valid cart items supplied."}, status=400)

    summary = _serialize_cart(_cart_queryset(request))
    return JsonResponse({
        "success": True,
        "added": added,
        "cart": summary,
    })


@require_GET
def cart_summary(request):
    """Return a lightweight JSON summary of the current cart."""
    summary = _serialize_cart(_cart_queryset(request))
    return JsonResponse(summary)
