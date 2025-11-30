from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_home, name='booking_home'),
    path('guest/add/', views.add_to_cart_guest, name='add_to_cart_guest'),
    path('guest/cart/', views.view_cart_guest, name='view_cart_guest'),
    path('guest/confirm/', views.confirm_guest_booking, name='confirm_guest_booking'),

    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/confirm/', views.confirm_cart, name='confirm_cart'),
    # Services copy inside bookings
    path('services/', views.services_home, name='booking_services'),
]
